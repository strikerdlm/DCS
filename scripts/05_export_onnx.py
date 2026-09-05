"""Export global/Mondrian single-regressor bundles with host postprocessing.

Checks final probabilities, intervals, and training-support gating using
complete physical profiles. CQR requires three graphs and is rejected; the
zero-inflated stack uses script 07. Dynamic INT8 tree-attribute quantization
is not implemented, and CPU batch timings are not wearable measurements.

Usage
-----
    python scripts/05_export_onnx.py \\
        --input-model artifacts/tinydcs_adrac_v0.5.joblib \\
        --output-onnx artifacts/tinydcs_adrac_v0.5.onnx \\
        --benchmark-n 10000 \\
        --tolerance 1e-4
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click
import numpy as np
import pandas as pd
from scipy.special import expit

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.evidence_common import (
    export_metadata,
    feasible_feature_matrix,
    host_ood,
    onnx_session,
    sha256,
    write_json,
)
from tinydcs.surrogate import (
    ConformalCalibration,
    MondrianConformalCalibration,
    TinyDcsSurrogate,
    ZeroInflatedCalibration,
)


def _validate_supported(surrogate):
    if isinstance(surrogate.conformal, ZeroInflatedCalibration):
        raise TypeError("Use scripts/07_export_zero_inflated_onnx.py for both zero-inflated stages")
    if not isinstance(surrogate.conformal, (ConformalCalibration, MondrianConformalCalibration)):
        raise TypeError("Single-graph export supports only global or Mondrian intervals; CQR requires all three graphs")


def _postprocess(logits, X, metadata):
    """Reproduce final probability intervals, including the training inverse."""
    q = np.full(len(logits), metadata["conformal_q"], dtype=float)
    if metadata["kind"] == "mondrian":
        column = metadata["feature_names"].index(metadata["mondrian_feature"])
        bands = np.floor((X[:, column]-metadata["mondrian_origin"])/metadata["mondrian_width"])
        for band, value in metadata["mondrian_quantiles"].items():
            q[bands == int(band)] = value
    n = metadata["target_transform_n"]
    def inverse(z):
        p = expit(z)
        return p if n is None else np.clip((p*max(n, 2)-.5)/(max(n, 2)-1), 0, 1)
    return {"point": inverse(logits), "lower": inverse(logits-q), "upper": inverse(logits+q)}


def _parity(surrogate, session, X, metadata, tolerance):
    logits = session.run(None, {session.get_inputs()[0].name: X.astype(np.float32)})[0].ravel()
    frame = pd.DataFrame(X, columns=surrogate.feature_names)
    reference = surrogate.predict(frame)
    actual = _postprocess(logits, X, metadata)
    delta = {key: float(np.max(np.abs(actual[key]-reference[key]))) for key in actual}
    delta["raw_logit"] = float(np.max(np.abs(logits-surrogate.model.predict(frame))))
    gate = host_ood(X, metadata)
    delta["ood_distance"] = float(np.max(np.abs(gate["ood_distance"]-reference["ood_distance"])))
    if max(delta.values()) > tolerance or not np.array_equal(gate["in_envelope"], reference["in_envelope"]):
        raise click.ClickException(f"Final ONNX probability/interval/support parity failed: {delta}")
    return {"max_abs_error": delta, "tolerance": tolerance, "n": len(X),
            "fixture_kind": "feasible constant-workload profiles; all dependent features recomputed",
            "support_gate_identical": True, "supported_n": int(gate["in_envelope"].sum()),
            "quantitative_output_n": int(gate["quantitative_output_enabled"].sum())}


def _convert_lightgbm_to_onnx(model, n_features: int):
    """Convert a LightGBM regressor to ONNX using onnxmltools."""
    from onnxconverter_common import FloatTensorType
    from onnxmltools import convert_lightgbm

    initial_types = [("input", FloatTensorType([None, n_features]))]
    # zipmap=False gives us a plain tensor output, which is what we want
    # for a regression model. Target opset 13 is broadly supported.
    return convert_lightgbm(
        model,
        initial_types=initial_types,
        target_opset=13,
        zipmap=False,
    )


def _random_feature_matrix(feature_names: list[str], n: int, seed: int = 1) -> np.ndarray:
    """Generate physical profiles before deriving the feature matrix."""
    return feasible_feature_matrix(feature_names, n, seed)


def _benchmark_onnx(sess, input_name: str, X: np.ndarray, n_warmup: int = 50) -> dict:
    """CPU batch latency and its arithmetic per-row amortization."""
    # Warm up.
    for _ in range(n_warmup):
        sess.run(None, {input_name: X})
    # Measure.
    n_trials = 20
    times = []
    for _ in range(n_trials):
        t0 = time.perf_counter()
        sess.run(None, {input_name: X})
        times.append(time.perf_counter() - t0)
    times = np.asarray(times, dtype=float)
    per_row_us = times / max(len(X), 1) * 1e6
    return {
        "batch_size": len(X),
        "trials": int(n_trials),
        "batch_latency_ms_p50": float(np.percentile(times, 50) * 1e3),
        "batch_latency_ms_p95": float(np.percentile(times, 95) * 1e3),
        "per_row_latency_us_p50": float(np.percentile(per_row_us, 50)),
        "per_row_latency_us_p95": float(np.percentile(per_row_us, 95)),
    }


@click.command()
@click.option("--input-model", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--output-onnx", type=click.Path(dir_okay=False), required=True)
@click.option("--output-int8", type=click.Path(dir_okay=False), default=None,
              help="Unsupported legacy option; tree INT8 conversion is rejected.")
@click.option("--benchmark-n", type=int, default=10_000, show_default=True,
              help="Batch size for latency benchmarking.")
@click.option("--tolerance", type=float, default=1e-4, show_default=True,
              help="Max per-prediction absolute error allowed between ONNX and Python ref.")
def main(
    input_model: str,
    output_onnx: str,
    output_int8: str | None,
    benchmark_n: int,
    tolerance: float,
) -> None:
    surrogate = TinyDcsSurrogate.load(input_model)
    try:
        _validate_supported(surrogate)
    except TypeError as exc:
        raise click.ClickException(str(exc)) from exc
    if benchmark_n < 1 or tolerance <= 0:
        raise click.ClickException("positive benchmark size and tolerance required")
    if output_int8:
        raise click.ClickException("Dynamic INT8 conversion does not quantize tree ensemble attributes; no INT8 claim or artifact is produced")
    feat = list(surrogate.feature_names)
    click.echo(f"Loaded surrogate with {len(feat)} features.")

    # 1. Convert LightGBM → ONNX.
    onnx_model = _convert_lightgbm_to_onnx(surrogate.model, n_features=len(feat))
    Path(output_onnx).parent.mkdir(parents=True, exist_ok=True)
    with open(output_onnx, "wb") as f:
        f.write(onnx_model.SerializeToString())
    onnx_size_kb = Path(output_onnx).stat().st_size / 1024
    click.echo(f"Wrote FP32 ONNX → {output_onnx} ({onnx_size_kb:.1f} KB).")

    # 2. Parity check vs Python.
    metadata = export_metadata(surrogate, input_model)
    calibration = surrogate.conformal
    if isinstance(calibration, MondrianConformalCalibration):
        metadata.update(kind="mondrian", conformal_q=calibration.global_q,
                        mondrian_feature=calibration.group_feature,
                        mondrian_width=calibration.band_width, mondrian_origin=calibration.band_origin,
                        mondrian_quantiles=calibration.group_quantiles)
    else:
        metadata.update(kind="global", conformal_q=calibration.q)
    metadata["runtime_algorithm"] = "p = clip((sigmoid(logit)*n-.5)/(n-1),0,1); apply same inverse at logit +/- conformal_q; n=target_transform_n"
    metadata["graph_sha256"] = sha256(output_onnx)
    sess = onnx_session(output_onnx)
    input_name = sess.get_inputs()[0].name
    X = _random_feature_matrix(feat, n=benchmark_n, seed=1)
    parity = _parity(surrogate, sess, X, metadata, tolerance)
    max_abs = parity["max_abs_error"]["raw_logit"]
    click.echo(f"Max |ONNX - Python| logit error across {benchmark_n} rows: {max_abs:.3e}")
    if max_abs > tolerance:
        raise click.ClickException(
            f"ONNX parity check failed: max |delta| = {max_abs:.3e} > tol = {tolerance:.0e}"
        )

    # 3. Benchmark FP32 ONNX.
    bench_fp32 = _benchmark_onnx(sess, input_name, X.astype(np.float32))
    bench_fp32["model_size_kb"] = onnx_size_kb

    # 5. Emit a JSON summary next to the ONNX file.
    summary = {
        "metadata": metadata,
        "parity": parity,
        "latency_interpretation": "CPU batch latency divided by batch size; not measured single-request, wearable, or MCU latency",
        "input_model": input_model,
        "n_features": len(feat),
        "feature_names": feat,
        "onnx_fp32": {
            "path": output_onnx,
            "size_kb": onnx_size_kb,
            "max_abs_logit_error_vs_python": max_abs,
            "benchmark_cpu": bench_fp32,
        },
        "onnx_int8_dynamic": None,
    }
    summary_path = Path(output_onnx).with_suffix(".onnx.benchmark.json")
    write_json(summary_path, summary)
    write_json(Path(output_onnx).with_suffix(".onnx.metadata.json"), metadata)
    click.echo(f"Summary → {summary_path}")
    click.echo(
        "\nHeadline:\n"
        f"  FP32 size = {onnx_size_kb:.1f} KB, "
        f"per-row p50 = {bench_fp32['per_row_latency_us_p50']:.2f} us, "
        f"p95 = {bench_fp32['per_row_latency_us_p95']:.2f} us"
    )


if __name__ == "__main__":
    main()
