"""Shared provenance, frozen partitions, and feasible export fixtures.

These utilities compare emulation of a model-generated grid. Grid dependence
precludes interpreting descriptive coverage intervals as clinical evidence.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import sys
from dataclasses import asdict
from importlib import metadata as packages
from pathlib import Path

import numpy as np
import pandas as pd

from tinydcs.features import extract_features
from tinydcs.simulator import ExposureProfile
from tinydcs.surrogate import partition_indices

ROOT = Path(__file__).resolve().parents[1]
PARTS = ("train", "cal", "test")
RELEASE_CRITERIA = {"max_mae": .03, "min_coverage": .94, "nominal": .95}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(value):
    # Keep the canonical encoding used in primary script 04.
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def environment():
    versions = {}
    for name in ("numpy", "pandas", "scipy", "scikit-learn", "lightgbm", "joblib",
                 "pyarrow", "onnx", "onnxruntime", "onnxmltools", "onnxconverter-common"):
        try:
            versions[name] = packages.version(name)
        except packages.PackageNotFoundError:
            versions[name] = None
    return {"python": sys.version, "platform": platform.platform(), "packages": versions,
            "threads": {k: os.environ.get(k) for k in
                        ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
            "onnxruntime_threads": 2, "lightgbm_threads": 2}


def cell_ids(df, partition):
    if "cell_id" not in df or df.cell_id.duplicated().any():
        raise ValueError("unique stable cell_id required for reproducible evidence")
    return {key: df.iloc[partition[key]].cell_id.astype(str).tolist() for key in PARTS}


def partition_from_ids(df, ids):
    """Map membership to local positions; allow cells omitted by a policy."""
    if df.cell_id.duplicated().any():
        raise ValueError("partitions must cover each row exactly once")
    lookup = {str(cell): i for i, cell in enumerate(df.cell_id)}
    parts = {key: np.asarray([lookup[cell] for cell in ids[key] if cell in lookup], dtype=int)
             for key in PARTS}
    flat = np.concatenate(list(parts.values()))
    if len(flat) != len(df) or not np.array_equal(np.sort(flat), np.arange(len(df))):
        raise ValueError("partitions must cover each row exactly once")
    return parts


def extend_partition(all_ids, frozen, seed=42):
    """Keep primary cells frozen; assign additional policy cells independently."""
    seen = {cell for key in PARTS for cell in frozen[key]}
    extras = np.asarray(sorted(set(all_ids) - seen))
    if not len(extras):
        return {k: list(frozen[k]) for k in PARTS}
    added = partition_indices(len(extras), seed=seed)
    return {k: list(frozen[k]) + extras[added[k]].tolist() for k in PARTS}


def grouped_partition(df, seed=42):
    """Hold out whole altitude/prebreathe/exercise profiles, including all times."""
    groups = df.apply(lambda row: json.dumps([float(row.altitude),
                      float(row.prebreathing_time), str(row.exercise_level)]), axis=1)
    unique = np.asarray(sorted(groups.unique()))
    group_split = partition_indices(len(unique), seed=seed)
    return ({k: np.flatnonzero(groups.isin(unique[idx]).to_numpy())
             for k, idx in group_split.items()}, groups)


def augment(df, seed=42):
    spec = importlib.util.spec_from_file_location("train04_evidence", ROOT / "scripts/04_train_adrac_surrogate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._augment_with_vo2(df, seed=seed)


def prepare_data(training, seed=42, reference_metrics=None):
    path = Path(training)
    raw = (pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)).reset_index(drop=True)
    partition = partition_indices(len(raw), seed=seed)
    ids = cell_ids(raw, partition)
    dataset_id, split_id = sha256(path), identity(ids)
    if reference_metrics:
        ref = Path(reference_metrics)
        metrics = json.loads(ref.read_text())
        metadata = metrics["metadata"]
        if metadata["dataset_id"] != dataset_id or metadata["split_id"] != split_id:
            raise ValueError("reference dataset or frozen partition does not match")
        if json.loads(ref.with_suffix(".splits.json").read_text()) != ids:
            raise ValueError("frozen cell identifiers do not match reference split")
        augmented = pd.read_parquet(ref.with_suffix(".features.parquet"))
        if (not augmented.index.equals(raw.index) or
                not np.array_equal(augmented.pdcs_adrac_target.to_numpy(),
                                   raw.risk_of_decompression_sickness.to_numpy()/100)):
            raise ValueError("cached feature rows do not match raw cells and targets")
    else:
        augmented = augment(raw, seed=seed)
    return raw, augmented, partition, ids


def evidence_metadata(training, ids, config, features, kind, *, metrics=None, seed=42):
    dataset_id, split_id = sha256(training), identity(ids)
    settings = asdict(config) if hasattr(config, "__dataclass_fields__") else config
    payload = {"dataset_id": dataset_id, "split_id": split_id, "training_config": settings,
               "feature_names": list(features), "calibration_mode": kind}
    passed = bool(metrics and metrics["point"]["mae"] <= RELEASE_CRITERIA["max_mae"]
                  and metrics["coverage"]["coverage"] >= RELEASE_CRITERIA["min_coverage"])
    return payload | {
        "schema_version": "accuracy-v3", "model_id": identity(payload)[:20],
        "target_kind": "model_probability", "target_unit": "probability",
        "clinical_validation": False, "interval_kind": "split_conformal_model_agreement",
        "vo2_provenance": "synthetic Rest/Mild/Heavy augmentation; no measured continuous VO2",
        "split": {"seed": seed, "train": .65, "cal": .20, "test": .15},
        "partition_counts": {k: len(ids[k]) for k in PARTS},
        "partition_cell_id_sha256": {k: identity(ids[k]) for k in PARTS},
        "release_criteria": RELEASE_CRITERIA, "quantitative_enabled": passed,
        "coverage_interpretation": "descriptive model-grid coverage; dependent rows are not IID clinical observations",
        "environment": environment(), "command": [sys.executable, *sys.argv],
    }


def feasible_feature_matrix(feature_names, n, seed=1):
    if n < 1:
        raise ValueError("at least one feasible profile is required")
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        profile = ExposureProfile(target_altitude_ft=float(rng.uniform(18000, 40000)),
                                  prebreathe_duration_min=float(rng.uniform(0, 60)),
                                  altitude_duration_min=float(rng.uniform(10, 240)),
                                  altitude_i_ex_trajectory=float(rng.uniform(0, 1.5)))
        record = asdict(extract_features(profile))
        rows.append([record[name] for name in feature_names])
    return np.asarray(rows, dtype=float)


def export_metadata(surrogate, input_model):
    return {"version": "accuracy-v3", "evidence": surrogate.metadata,
            "source_model_sha256": sha256(input_model), "environment": environment(),
            "feature_names": list(surrogate.feature_names),
            "target_transform_n": surrogate.target_transform_n,
            "confidence": surrogate.conformal.confidence,
            "ood_mean": surrogate.ood.mean.tolist(),
            "ood_inv_cov": surrogate.ood.inv_cov.tolist(),
            "ood_scale": surrogate.ood.scale.tolist(),
            "ood_threshold": float(surrogate.ood.threshold),
            "ood_minimum": surrogate.ood.minimum.tolist(),
            "ood_maximum": surrogate.ood.maximum.tolist(),
            "ood_bound_tolerance": "1e-8 * maximum(ood_maximum - ood_minimum, 1e-8)",
            "ood_input_precision": "validate original float64 features before float32 graph conversion",
            "input_validation": "finite features in declared units from complete physical profile",
            "output_gate": "quantitative_enabled AND training-support distance AND observed feature bounds",
            "interval_kind": "split_conformal_model_agreement"}


def host_ood(X, metadata):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != len(metadata["feature_names"]) or not np.isfinite(X).all():
        raise ValueError("features must be a finite matrix of trained width")
    diff = (X-np.asarray(metadata["ood_mean"]))/np.asarray(metadata["ood_scale"])
    distance = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", diff, metadata["ood_inv_cov"], diff), 0))
    low, high = np.asarray(metadata["ood_minimum"]), np.asarray(metadata["ood_maximum"])
    tol = 1e-8 * np.maximum(high-low, 1e-8)
    accepted = (distance <= metadata["ood_threshold"]) & np.all((X >= low-tol) & (X <= high+tol), axis=1)
    return {"ood_distance": distance, "in_envelope": accepted,
            "quantitative_output_enabled": accepted & bool(metadata["evidence"].get("quantitative_enabled", False))}


def onnx_session(path):
    import onnxruntime as ort
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 2
    return ort.InferenceSession(str(path), sess_options=options, providers=["CPUExecutionProvider"])
