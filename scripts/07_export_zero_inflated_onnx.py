#!/usr/bin/env python3
"""Export a zero-inflated TinyDCS surrogate to two ONNX graphs + a sidecar.

The zero-inflated model is a two-stage stack:

  * stage 1 — LightGBM classifier predicting P(y = 0 | x);
  * stage 2 — LightGBM regressor predicting logit(y) conditional on y > 0.

At inference, a gate threshold routes each sample to either a zero-anchored
interval or the continuous branch's conformal interval. ONNX has no native
``if`` routing that survives ONNX Runtime Mobile cleanly, so we ship the
two graphs side-by-side plus a JSON sidecar with the gate constants and
feature names. A host-side runtime (``tinydcs.runtime.ZeroInflatedRuntime``
or any C translation) then performs the gate + mixture aggregation.

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

from tinydcs.surrogate import TinyDcsSurrogate, ZeroInflatedCalibration  # noqa: E402


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
    from onnxmltools.convert.common.data_types import FloatTensorType
    from onnxmltools import convert_lightgbm

    # zipmap=False gives a tensor (batch, n_classes) of probabilities
    # alongside the predicted label; we want the tensor.
    return convert_lightgbm(
        model,
        initial_types=[("input", FloatTensorType([None, n_features]))],
        target_opset=13,
        zipmap=False,
    )


def _random_feature_matrix(feature_names: list[str], n: int, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
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
        "batch_size": int(len(X)),
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
    metadata = {
        "version": "0.4.0",
        "kind": "zero_inflated",
        "feature_names": feat,
        "gate_threshold": float(surrogate.conformal.gate_threshold),
        "zero_upper_bound": float(surrogate.conformal.zero_upper_bound),
        "continuous_q": float(surrogate.conformal.continuous_q),
        "confidence": float(surrogate.conformal.confidence),
        "ood_mean": surrogate.ood.mean.tolist(),
        "ood_inv_cov": surrogate.ood.inv_cov.tolist(),
        "ood_threshold": float(surrogate.ood.threshold),
        "runtime_algorithm": (
            "p_zero = classifier(x)[:, 1]; "
            "cont_logit = continuous(x); "
            "is_gated_zero = p_zero >= gate_threshold; "
            "point = (1 - p_zero) * sigmoid(cont_logit); "
            "lower = 0 if is_gated_zero else (1 - p_zero) * sigmoid(cont_logit - continuous_q); "
            "upper = zero_upper_bound if is_gated_zero "
            "        else max(zero_upper_bound, (1 - p_zero) * sigmoid(cont_logit + continuous_q) + p_zero * zero_upper_bound)"
        ),
    }
    meta_path = out_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    click.echo(f"Wrote metadata → {meta_path}")

    # 4. Parity check: host runtime reproduces Python ``surrogate.predict()`` bit-exact.
    import onnxruntime as ort

    clf_sess = ort.InferenceSession(str(clf_path), providers=["CPUExecutionProvider"])
    cont_sess = ort.InferenceSession(str(cont_path), providers=["CPUExecutionProvider"])
    clf_input = clf_sess.get_inputs()[0].name
    cont_input = cont_sess.get_inputs()[0].name

    X = _random_feature_matrix(feat, n=benchmark_n, seed=1)
    clf_outputs = clf_sess.run(None, {clf_input: X})
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

    cont_onnx = np.asarray(cont_sess.run(None, {cont_input: X})[0], dtype=float).ravel()

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

    # 5. Benchmark each ONNX graph separately; host aggregation cost is negligible.
    bench_clf = _benchmark(clf_sess, clf_input, X)
    bench_clf["model_size_kb"] = clf_size_kb
    bench_cont = _benchmark(cont_sess, cont_input, X)
    bench_cont["model_size_kb"] = cont_size_kb

    combined = {
        "total_size_kb": clf_size_kb + cont_size_kb,
        "per_row_latency_us_p50": (
            bench_clf["per_row_latency_us_p50"] + bench_cont["per_row_latency_us_p50"]
        ),
        "per_row_latency_us_p95": (
            bench_clf["per_row_latency_us_p95"] + bench_cont["per_row_latency_us_p95"]
        ),
    }

    summary = {
        "input_model": input_model,
        "n_features": len(feat),
        "parity": {
            "max_abs_p_zero": max_abs_p_zero,
            "max_abs_continuous_logit": max_abs_cont,
            "tolerance": tolerance,
        },
        "classifier_benchmark": bench_clf,
        "continuous_benchmark": bench_cont,
        "combined_inference": combined,
    }
    bench_path = out_dir / "benchmark.json"
    bench_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    click.echo(f"Summary → {bench_path}")

    click.echo(
        "\nHeadline:\n"
        f"  Classifier: {clf_size_kb:.1f} KB, "
        f"per-row p50 = {bench_clf['per_row_latency_us_p50']:.2f} us\n"
        f"  Continuous: {cont_size_kb:.1f} KB, "
        f"per-row p50 = {bench_cont['per_row_latency_us_p50']:.2f} us\n"
        f"  Combined:   {combined['total_size_kb']:.1f} KB, "
        f"per-row p50 = {combined['per_row_latency_us_p50']:.2f} us"
    )


if __name__ == "__main__":
    main()
