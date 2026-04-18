#!/usr/bin/env python3
"""Export a trained TinyDCS LightGBM surrogate to ONNX, benchmark it, and
optionally apply dynamic INT8 quantization.

This script closes the Paper-1 "runs on wearables" objective (O4 in README):

  1. Loads a TinyDcsSurrogate joblib (produced by scripts/03 or 04).
  2. Converts the LightGBM regressor to ONNX via onnxmltools.
  3. Verifies parity with the Python reference within a configurable tolerance.
  4. Benchmarks CPU inference latency (as a proxy for embedded targets).
  5. Optionally produces a dynamically quantized (INT8) ONNX model and
     re-benchmarks it.

Notes
-----
* Only the LightGBM backbone is exported. The split-conformal quantile and
  the Mahalanobis OOD detector are cheap post-processing; on-device they are
  trivially reproduced from the saved surrogate metadata.
* Dynamic quantization is the least-intrusive choice for LightGBM-as-ONNX
  and works on ARM with ONNX Runtime Mobile. For static INT8 (smaller flash
  footprint), a calibration dataset is required; see the TODO.

Usage
-----
    python scripts/05_export_onnx.py \\
        --input-model artifacts/tinydcs_adrac_v0.5.joblib \\
        --output-onnx artifacts/tinydcs_adrac_v0.5.onnx \\
        --output-int8 artifacts/tinydcs_adrac_v0.5.int8.onnx \\
        --benchmark-n 10000 \\
        --tolerance 1e-4
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import click
import numpy as np

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tinydcs.surrogate import TinyDcsSurrogate  # noqa: E402


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
    """Sample a plausible feature batch inside the training envelope."""
    rng = np.random.default_rng(seed)
    # Use envelope-consistent distributions so benchmarks reflect realistic inputs.
    specs = {
        "altitude_ft": (18000, 40000),
        "ambient_pressure_atm": (0.18, 0.52),
        "prebreathe_time_min": (0, 180),
        "prebreathe_fio2": (0.85, 1.0),
        "ascent_rate_fpm": (500, 5000),
        "altitude_time_min": (10, 240),
        "altitude_fio2": (0.21, 1.0),
        "prebreathe_vo2_mean_lmin": (0, 0.5),
        "prebreathe_vo2_peak_lmin": (0, 1.0),
        "altitude_vo2_mean_lmin": (0, 1.0),
        "altitude_vo2_peak_1min_lmin": (0, 1.5),
        "altitude_vo2_integral_lmin_min": (0, 250),
        "tissue_n2_ratio_360min": (1.0, 4.0),
    }
    cols = []
    for name in feature_names:
        lo, hi = specs.get(name, (0.0, 1.0))
        cols.append(rng.uniform(lo, hi, size=n).astype(np.float32))
    return np.stack(cols, axis=1)


def _benchmark_onnx(sess, input_name: str, X: np.ndarray, n_warmup: int = 50) -> dict:
    """Report latency percentiles per inference (single-batch).

    The benchmark uses the full batch. For mobile/MCU the per-row latency is
    the load-bearing metric, so we also divide.
    """
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
        "batch_size": int(len(X)),
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
              help="If provided, also write a dynamically-quantized INT8 model.")
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
    import onnxruntime as ort

    sess = ort.InferenceSession(output_onnx, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    X = _random_feature_matrix(feat, n=benchmark_n, seed=1)
    onnx_logit = sess.run(None, {input_name: X})[0].ravel()
    py_logit = np.asarray(surrogate.model.predict(X), dtype=float).ravel()
    max_abs = float(np.max(np.abs(onnx_logit - py_logit)))
    click.echo(f"Max |ONNX - Python| logit error across {benchmark_n} rows: {max_abs:.3e}")
    if max_abs > tolerance:
        raise click.ClickException(
            f"ONNX parity check failed: max |delta| = {max_abs:.3e} > tol = {tolerance:.0e}"
        )

    # 3. Benchmark FP32 ONNX.
    bench_fp32 = _benchmark_onnx(sess, input_name, X)
    bench_fp32["model_size_kb"] = onnx_size_kb

    # 4. Optional INT8 quantization.
    bench_int8: dict | None = None
    int8_size_kb: float | None = None
    if output_int8:
        from onnxruntime.quantization import QuantType, quantize_dynamic

        Path(output_int8).parent.mkdir(parents=True, exist_ok=True)
        quantize_dynamic(
            model_input=output_onnx,
            model_output=output_int8,
            weight_type=QuantType.QInt8,
        )
        int8_size_kb = Path(output_int8).stat().st_size / 1024
        click.echo(f"Wrote INT8-dynamic ONNX → {output_int8} ({int8_size_kb:.1f} KB).")
        sess_q = ort.InferenceSession(output_int8, providers=["CPUExecutionProvider"])
        input_name_q = sess_q.get_inputs()[0].name
        q_logit = sess_q.run(None, {input_name_q: X})[0].ravel()
        max_abs_q = float(np.max(np.abs(q_logit - py_logit)))
        click.echo(f"Max |INT8 - Python| logit error: {max_abs_q:.3e}")
        bench_int8 = _benchmark_onnx(sess_q, input_name_q, X)
        bench_int8["model_size_kb"] = int8_size_kb
        bench_int8["max_abs_logit_error_vs_python"] = max_abs_q

    # 5. Emit a JSON summary next to the ONNX file.
    summary = {
        "input_model": input_model,
        "n_features": len(feat),
        "feature_names": feat,
        "onnx_fp32": {
            "path": output_onnx,
            "size_kb": onnx_size_kb,
            "max_abs_logit_error_vs_python": max_abs,
            "benchmark_cpu": bench_fp32,
        },
        "onnx_int8_dynamic": (
            {
                "path": output_int8,
                "size_kb": int8_size_kb,
                "benchmark_cpu": bench_int8,
            }
            if output_int8 else None
        ),
    }
    summary_path = Path(output_onnx).with_suffix(".onnx.benchmark.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    click.echo(f"Summary → {summary_path}")
    click.echo(
        "\nHeadline:\n"
        f"  FP32 size = {onnx_size_kb:.1f} KB, "
        f"per-row p50 = {bench_fp32['per_row_latency_us_p50']:.2f} us, "
        f"p95 = {bench_fp32['per_row_latency_us_p95']:.2f} us"
    )
    if bench_int8:
        click.echo(
            f"  INT8 size = {int8_size_kb:.1f} KB, "
            f"per-row p50 = {bench_int8['per_row_latency_us_p50']:.2f} us, "
            f"p95 = {bench_int8['per_row_latency_us_p95']:.2f} us"
        )


if __name__ == "__main__":
    main()
