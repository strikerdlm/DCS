"""Export a zero-inflated TinyDCS surrogate to two ONNX graphs + a sidecar.

The zero-inflated model is a two-stage stack:

  * stage 1 — LightGBM classifier predicting P(y = 0 | x);
  * stage 2 — LightGBM regressor predicting logit(y) conditional on y > 0.

The host computes (1-P(zero))*sigmoid(continuous_logit), then applies the
probability-scale conformal quantile calibrated on that final mixture.
Both graphs and their exact postprocessing/support metadata are exported.
The benchmark runs on this host CPU; it is not a wearable hardware result.

This keeps each ONNX graph small (tree ensembles quantize cleanly) and
makes the two sub-models independently benchmarkable.

Usage
-----
    python scripts/07_export_zero_inflated_onnx.py \\
        --input-model artifacts/tinydcs_adrac_zi.joblib \\
        --output-dir artifacts/zi_onnx \\
        --benchmark-n 10000 --tolerance 1e-4

Produces ``zi_onnx/classifier.onnx``, ``zi_onnx/continuous.onnx``,
``zi_onnx/metadata.json``, and ``zi_onnx/benchmark.json``.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click
import numpy as np
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
from tinydcs.surrogate import TinyDcsSurrogate, ZeroInflatedCalibration


def _convert_regressor(model, n_features: int):
    from onnxconverter_common import FloatTensorType
    from onnxmltools import convert_lightgbm

    return convert_lightgbm(
        model,
        initial_types=[("input", FloatTensorType([None, n_features]))],
        target_opset=13,
        zipmap=False,
    )


def _convert_classifier(model, n_features: int):
    # The LightGBM classifier shape calculator in onnxmltools demands its
    # own FloatTensorType variant (not the generic onnxconverter_common one).
    from onnxmltools import convert_lightgbm
    from onnxmltools.convert.common.data_types import FloatTensorType

    # zipmap=False gives a tensor (batch, n_classes) of probabilities
    # alongside the predicted label; we want the tensor.
    return convert_lightgbm(
        model,
        initial_types=[("input", FloatTensorType([None, n_features]))],
        target_opset=13,
        zipmap=False,
    )


def _random_feature_matrix(feature_names: list[str], n: int, seed: int = 1) -> np.ndarray:
    """Feasible constant-workload profiles, with dependent features recomputed."""
    return feasible_feature_matrix(feature_names, n, seed)


def _host_predict(clf_session, cont_session, X, metadata):
    query = X.astype(np.float32)
    outputs = clf_session.run(None, {clf_session.get_inputs()[0].name: query})
    probability = next((np.asarray(out) for out in outputs
                        if np.asarray(out).ndim == 2 and np.asarray(out).shape[1] == 2), None)
    if probability is None:
        raise ValueError("classifier did not return the two-class probability tensor")
    p_zero = probability[:, 1].astype(float)
    continuous = np.asarray(cont_session.run(None, {cont_session.get_inputs()[0].name: query})[0], dtype=float).ravel()
    point = (1-p_zero)*expit(continuous)
    q = metadata["probability_q"]
    return {"point": point, "lower": np.maximum(0, point-q), "upper": np.minimum(1, point+q),
            "p_zero": p_zero, "continuous_logit": continuous} | host_ood(X, metadata)


def _benchmark_host(clf, cont, X, metadata, trials=20):
    for _ in range(5):
        _host_predict(clf, cont, X, metadata)
    elapsed = []
    for _ in range(trials):
        start = time.perf_counter()
        _host_predict(clf, cont, X, metadata)
        elapsed.append((time.perf_counter()-start)*1e3)
    return {"batch_size": len(X), "trials": trials,
            "latency_ms_p50": float(np.percentile(elapsed, 50)),
            "latency_ms_p95": float(np.percentile(elapsed, 95)),
            "scope": "both ONNX graphs, float32 conversion, mixture, interval, support gate; features already extracted"}


def _benchmark(sess, input_name: str, X: np.ndarray, n_warmup: int = 50, n_trials: int = 20) -> dict:
    for _ in range(n_warmup):
        sess.run(None, {input_name: X})
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
@click.option("--output-dir", type=click.Path(file_okay=False), required=True)
@click.option("--benchmark-n", type=int, default=10_000, show_default=True)
@click.option("--tolerance", type=float, default=1e-4, show_default=True)
def main(input_model: str, output_dir: str, benchmark_n: int, tolerance: float) -> None:
    if benchmark_n < 1 or tolerance <= 0:
        raise click.ClickException("positive benchmark size and tolerance required")
    surrogate = TinyDcsSurrogate.load(input_model)
    if not isinstance(surrogate.conformal, ZeroInflatedCalibration):
        raise click.ClickException(
            f"Input model does not carry a ZeroInflatedCalibration "
            f"(got {type(surrogate.conformal).__name__}). Use scripts/05_export_onnx.py "
            f"for single-model surrogates."
        )

    feat = list(surrogate.feature_names)
    click.echo(f"Loaded zero-inflated surrogate with {len(feat)} features.")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export stage 1 (classifier).
    onnx_clf = _convert_classifier(surrogate.conformal.zero_classifier, n_features=len(feat))
    # onnxmltools currently hard-codes label batch size 1; both outputs accept
    # arbitrary batches. Declare the symbolic batch dimension truthfully.
    for output in onnx_clf.graph.output:
        dimension = output.type.tensor_type.shape.dim[0]
        dimension.ClearField("dim_value")
        dimension.dim_param = "batch"
    clf_path = out_dir / "classifier.onnx"
    with open(clf_path, "wb") as f:
        f.write(onnx_clf.SerializeToString())
    clf_size_kb = clf_path.stat().st_size / 1024
    click.echo(f"Wrote classifier ONNX → {clf_path} ({clf_size_kb:.1f} KB).")

    # 2. Export stage 2 (continuous regressor).
    onnx_cont = _convert_regressor(surrogate.conformal.continuous_model, n_features=len(feat))
    cont_path = out_dir / "continuous.onnx"
    with open(cont_path, "wb") as f:
        f.write(onnx_cont.SerializeToString())
    cont_size_kb = cont_path.stat().st_size / 1024
    click.echo(f"Wrote continuous ONNX → {cont_path} ({cont_size_kb:.1f} KB).")

    # 3. Metadata sidecar — everything the host runtime needs.
    metadata = export_metadata(surrogate, input_model) | {
        "version": "accuracy-v3",
        "evidence": surrogate.metadata,
        "kind": "zero_inflated",
        "feature_names": feat,
        "probability_q": float(surrogate.conformal.probability_q),
        "confidence": float(surrogate.conformal.confidence),
        "ood_mean": surrogate.ood.mean.tolist(),
        "ood_inv_cov": surrogate.ood.inv_cov.tolist(),
        "ood_threshold": float(surrogate.ood.threshold),
        "ood_scale": surrogate.ood.scale.tolist(),
        "ood_minimum": surrogate.ood.minimum.tolist(),
        "ood_maximum": surrogate.ood.maximum.tolist(),
        "interval_kind": "split_conformal_model_agreement",
        "input_validation": "finite features, declared units, complete profile; reject malformed inputs",
        "output_gate": "quantitative output only if evidence.quantitative_enabled and training-support distance AND feature bounds pass",
        "ood_algorithm": "d=(x-ood_mean)/ood_scale; sqrt(max(d.T @ ood_inv_cov @ d,0)) <= ood_threshold AND ood_minimum-tolerance <= x <= ood_maximum+tolerance",
        "runtime_algorithm": (
            "p_zero = classifier(x)[:, 1]; "
            "cont_logit = continuous(x); "
            "point = (1 - p_zero) * sigmoid(cont_logit); "
            "lower = max(0, point - probability_q); "
            "upper = min(1, point + probability_q)"

        ),
    }
    metadata["graph_sha256"] = {"classifier.onnx": sha256(clf_path), "continuous.onnx": sha256(cont_path)}

    # 4. Check numerical parity of stages, final intervals, and support gating.
    clf_sess = onnx_session(clf_path)
    cont_sess = onnx_session(cont_path)
    clf_input = clf_sess.get_inputs()[0].name
    cont_input = cont_sess.get_inputs()[0].name

    X = _random_feature_matrix(feat, n=benchmark_n, seed=1)
    clf_outputs = clf_sess.run(None, {clf_input: X.astype(np.float32)})
    # onnxmltools emits two outputs for a binary classifier: labels and probabilities.
    probs = None
    for out in clf_outputs:
        arr = np.asarray(out)
        if arr.ndim == 2 and arr.shape[1] == 2:
            probs = arr
            break
    if probs is None:
        raise click.ClickException("Could not locate probability tensor in classifier ONNX outputs")
    p_zero_onnx = probs[:, 1].astype(float).ravel()

    cont_onnx = np.asarray(cont_sess.run(None, {cont_input: X.astype(np.float32)})[0], dtype=float).ravel()

    # Python reference from the joblib.
    import pandas as pd

    X_df = pd.DataFrame(X, columns=feat)
    py_pred = surrogate.predict(X_df)
    p_zero_py = py_pred["p_zero"]
    cont_py = np.asarray(surrogate.conformal.continuous_model.predict(X_df), dtype=float).ravel()

    max_abs_p_zero = float(np.max(np.abs(p_zero_onnx - p_zero_py)))
    max_abs_cont = float(np.max(np.abs(cont_onnx - cont_py)))
    click.echo(f"Max |ONNX - Python| on P(y=0):           {max_abs_p_zero:.3e}")
    click.echo(f"Max |ONNX - Python| on continuous logit: {max_abs_cont:.3e}")
    if max_abs_p_zero > tolerance or max_abs_cont > tolerance:
        raise click.ClickException(
            f"Parity check failed: P(y=0) max-abs {max_abs_p_zero:.3e}, "
            f"continuous max-abs {max_abs_cont:.3e}, tol {tolerance:.0e}"
        )

    point_onnx = (1-p_zero_onnx)*expit(cont_onnx)
    q = surrogate.conformal.probability_q
    max_abs_probability = max(float(np.max(np.abs(py_pred[key]-actual))) for key, actual in
                              [("point", point_onnx), ("lower", np.maximum(0, point_onnx-q)),
                               ("upper", np.minimum(1, point_onnx+q))])
    if max_abs_probability > tolerance:
        raise click.ClickException("Final mixture/interval probability parity failed")
    actual = _host_predict(clf_sess, cont_sess, X, metadata)
    errors = {key: float(np.max(np.abs(py_pred[key]-actual[key])))
              for key in ("point", "lower", "upper", "ood_distance")}
    if max(errors.values()) > tolerance or not np.array_equal(actual["in_envelope"], py_pred["in_envelope"]):
        raise click.ClickException(f"Host probability/bounds/support gate parity failed: {errors}")
    write_json(out_dir / "metadata.json", metadata)

    # 5. Measure components and the complete host path separately.
    bench_clf = _benchmark(clf_sess, clf_input, X.astype(np.float32))
    bench_clf["model_size_kb"] = clf_size_kb
    bench_cont = _benchmark(cont_sess, cont_input, X.astype(np.float32))
    bench_cont["model_size_kb"] = cont_size_kb

    combined = {
        "total_size_kb": clf_size_kb + cont_size_kb,
        "sum_amortized_component_us_p50": (
            bench_clf["per_row_latency_us_p50"] + bench_cont["per_row_latency_us_p50"]
        ),
        "sum_amortized_component_us_p95_not_end_to_end": (
            bench_clf["per_row_latency_us_p95"] + bench_cont["per_row_latency_us_p95"]
        ),
    }

    summary = {
        "metadata": metadata,
        "input_model": input_model,
        "n_features": len(feat),
        "parity": {
            "max_abs_p_zero": max_abs_p_zero,
            "max_abs_probability_and_interval": max_abs_probability,
            "fixture_kind": "feasible constant-workload profiles",
            "max_abs_continuous_logit": max_abs_cont,
            "tolerance": tolerance,
            "n": len(X), "final_output_max_abs_error": errors,
            "support_gate_identical": True,
            "supported_n": int(actual["in_envelope"].sum()),
            "quantitative_output_n": int(actual["quantitative_output_enabled"].sum()),
        },
        "classifier_benchmark": bench_clf,
        "continuous_benchmark": bench_cont,
        "combined_inference": combined,
        "end_to_end_batch": _benchmark_host(clf_sess, cont_sess, X, metadata),
        "end_to_end_single_row": _benchmark_host(clf_sess, cont_sess, X[:1], metadata, trials=100),
        "latency_interpretation": "CPU only; component per-row numbers amortize a batch; single-row timings include both graphs and host postprocessing",
    }
    bench_path = out_dir / "benchmark.json"
    write_json(bench_path, summary)
    click.echo(f"Summary → {bench_path}")

    click.echo(
        "\nHeadline:\n"
        f"  Classifier: {clf_size_kb:.1f} KB, "
        f"per-row p50 = {bench_clf['per_row_latency_us_p50']:.2f} us\n"
        f"  Continuous: {cont_size_kb:.1f} KB, "
        f"per-row p50 = {bench_cont['per_row_latency_us_p50']:.2f} us\n"
        f"  Combined:   {combined['total_size_kb']:.1f} KB, "
        f"per-row p50 = {combined['sum_amortized_component_us_p50']:.2f} us"
    )


if __name__ == "__main__":
    main()
