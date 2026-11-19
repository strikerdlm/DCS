"""Fit research baselines and audit the external cohorts against the frozen v1 estimand."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sqlite3
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.special import betaln, digamma, expit, log_expit, logit
from scipy.stats import t

from scripts.build_chamber_database import DATA, DEFAULT_OUTPUT, ROOT, populate, publish, sha256
from tinydcs.study_models import GROUP, group_estimate, read_study


def family_blocks(rows):
    """Place families sharing any complete published model-input tuple in one fold."""
    families = {r["family"] for r in rows}
    connected = [{f} for f in sorted(families)]
    settings = defaultdict(set)
    for r in rows:
        settings[
            (r["pressure_psia"], r["duration_hours"], r["mean_tr360"], r["table2_ambulatory"])
        ].add(r["family"])
    for shared in settings.values():
        merged = set(shared)
        for group in connected:
            if group & shared:
                merged |= group
        connected = [g for g in connected if not g & shared] + [merged]
    return np.array(
        [next("+".join(sorted(g)) for g in connected if r["family"] in g) for r in rows]
    )


def beta_binomial(n, y, families):
    """Integrate the binomial likelihood over one latent event rate per protocol family."""
    _, codes = np.unique(families, return_inverse=True)
    cases = np.bincount(codes, weights=y)
    others = np.bincount(codes, weights=n - y)

    def loss(theta):
        a, b = np.exp(theta)
        ll = betaln(cases + a, others + b) - betaln(a, b)
        shared = digamma(a + b) - digamma(cases + others + a + b)
        grad = [
            a * np.sum(digamma(cases + a) - digamma(a) + shared),
            b * np.sum(digamma(others + b) - digamma(b) + shared),
        ]
        return -ll.sum(), -np.asarray(grad)

    result = minimize(
        loss,
        np.log([1.0, 5.0]),
        jac=True,
        method="L-BFGS-B",
        bounds=[(-8, 12), (-8, 12)],
        options={"ftol": 1e-12},
    )
    if not result.success:
        raise ValueError(f"Beta-binomial fit failed: {result.message}")
    a, b = np.exp(result.x)
    return {"alpha": float(a), "beta": float(b), "new_family_fraction": float(a / (a + b))}


def ridge(n, y, x):
    center = np.average(x, weights=n, axis=0)
    scale = np.sqrt(np.average((x - center) ** 2, weights=n, axis=0))
    scale[scale < 1e-12] = 1
    design = np.column_stack((np.ones(len(x)), (x - center) / scale))

    def loss(coef):
        eta = design @ coef
        penalty = np.r_[0.0, coef[1:]]
        value = (n * np.logaddexp(0.0, eta) - y * eta).sum() + 0.5 * penalty @ penalty
        return value, design.T @ (n * expit(eta) - y) + penalty

    result = minimize(
        loss,
        np.zeros(design.shape[1]),
        jac=True,
        method="L-BFGS-B",
        options={"ftol": 1e-13, "maxiter": 500},
    )
    if not result.success:
        raise ValueError(f"Grouped ridge fit failed: {result.message}")
    return {"coefficients": result.x.tolist(), "center": center.tolist(), "scale": scale.tolist()}


def ridge_predict(model, x):
    standardized = (x - model["center"]) / model["scale"]
    return expit(model["coefficients"][0] + standardized @ model["coefficients"][1:])


def scores(n, y, p):
    n_total, events, expected = n.sum(), y.sum(), n @ p
    return {
        "exposures": int(n_total),
        "observed": int(events),
        "expected": float(expected),
        "observed_to_expected": float(events / expected),
        "log_loss": float(-np.sum(y * np.log(p) + (n - y) * np.log1p(-p)) / n_total),
        "brier": float(np.sum(y * (1 - p) ** 2 + (n - y) * p**2) / n_total),
    }


def calibration(n, y, p, blocks):
    bins = np.digitize(p, [0.1, 0.25, 0.5, 0.75])
    curve = []
    for idx, bounds in enumerate(zip([0, 0.1, 0.25, 0.5, 0.75], [0.1, 0.25, 0.5, 0.75, 1])):
        take = bins == idx
        if np.any(take):
            curve.append(
                {
                    "bin": list(bounds),
                    "exposures": int(n[take].sum()),
                    "observed_fraction": float(y[take].sum() / n[take].sum()),
                    "predicted_fraction": float(np.average(p[take], weights=n[take])),
                }
            )
    if all(np.ptp(p[blocks == b]) == 0 for b in np.unique(blocks)):
        return {
            "bins": curve,
            "joint_intercept_slope": None,
            "reason": "A new-family prevalence is constant within each held-out block.",
        }
    x = np.column_stack((np.ones(len(p)), logit(p)))

    def loss(b):
        eta = x @ b
        return (n * np.logaddexp(0.0, eta) - y * eta).sum(), x.T @ (n * expit(eta) - y)

    result = minimize(loss, [0.0, 1.0], jac=True, method="BFGS")
    return {"bins": curve, "joint_intercept_slope": result.x.tolist() if result.success else None}


def cross_validate(n, y, blocks, pair, active):
    baseline = np.full(len(n), np.nan)
    challenger = baseline.copy()
    for block in np.unique(blocks[active]):
        test = active & (blocks == block)
        train = active & (blocks != block)
        baseline[test], challenger[test] = pair(train, test)
    return baseline[active], challenger[active]


def compare(n, y, blocks, identifiers, pair):
    active = np.ones(len(n), dtype=bool)
    base, alt = cross_validate(n, y, blocks, pair, active)
    baseline, challenger = scores(n, y, base), scores(n, y, alt)
    unique = np.unique(blocks)
    deleted = []
    for block in unique:
        keep = blocks != block
        p, q = cross_validate(n, y, blocks, pair, keep)
        deleted.append(
            scores(n[keep], y[keep], q)["log_loss"] - scores(n[keep], y[keep], p)["log_loss"]
        )
    se = np.sqrt((len(unique) - 1) * np.var(deleted))
    delta = challenger["log_loss"] - baseline["log_loss"]
    radius = float(t.ppf(0.975, len(unique) - 1) * se)
    return {
        "blocks": len(unique),
        "baseline": baseline,
        "challenger": challenger,
        "delta_log_loss": delta,
        "delete_block_refit_95": [delta - radius, delta + radius],
        "uncertainty": "Approximate t interval from deleting one complete block and repeating all folds and fits. Repeat-participant uncertainty is unidentified.",
        "internal_challenger_calibration": calibration(n, y, alt, blocks),
        "cross_fitted": [
            {
                "test_id": str(i),
                "block": str(b),
                "denominator": int(k),
                "observed": int(e),
                "baseline_fraction": float(p),
                "challenger_fraction": float(q),
            }
            for i, b, k, e, p, q in zip(identifiers, blocks, n, y, base, alt, strict=True)
        ],
    }


def nasa_study(db):
    rows = db.execute("SELECT * FROM development_counts ORDER BY test_id").fetchall()
    n = np.array([r["dcs_denominator"] for r in rows])
    y = np.array([r["dcs_cases"] for r in rows])
    families = np.array([r["family"] for r in rows])

    def predict(train, test):
        model = beta_binomial(n[train], y[train], families[train])
        return y[train].sum() / n[train].sum(), model["new_family_fraction"]

    return {
        "model": beta_binomial(n, y, families),
        "unit": "unseen NASA protocol-family mean",
        **compare(n, y, family_blocks(rows), [r["test_id"] for r in rows], predict),
    }


def afrl_study(db):
    rows = db.execute("SELECT * FROM afrl_test ORDER BY test_id").fetchall()
    n = np.array([r["exposures"] for r in rows])
    y = np.array([r["dcs_cases"] for r in rows])
    names = [
        "pressure_mmhg",
        "pb_including_ascent_min",
        "source_male",
        "mixed_gas_16_18",
        "retrospectively_assigned_max_vo2_ml_kg_min",
    ]
    x = np.array(
        [
            [
                r["pressure_mmhg"],
                r["pb_including_ascent_min"],
                r["source_sex"] == "M",
                r["test_id"] in (16, 18),
                r["assigned_max_vo2_ml_kg_min"],
            ]
            for r in rows
        ]
    )
    blocks = np.array([282 if r["pressure_mmhg"] == 281 else r["pressure_mmhg"] for r in rows])

    def predict(train, test):
        base = ridge(n[train], y[train], x[train, :-1])
        alt = ridge(n[train], y[train], x[train])
        return ridge_predict(base, x[test, :-1]), ridge_predict(alt, x[test])

    return {
        "horizon_h": 4,
        "features": names,
        "model": ridge(n, y, x),
        "unit": "AFRL four-hour test groups",
        "source_id": "afrl13",
        **compare(n, y, blocks, [r["test_id"] for r in rows], predict),
    }


def vge_check(db):
    frozen = json.loads((ROOT / "tinydcs/studies/grade-iv-vge-v1.json").read_bytes())
    rows = db.execute("SELECT * FROM vge_interval").fetchall()
    prefix = frozen["plan"]["split_prefix"]
    ordered = sorted(
        rows, key=lambda r: hashlib.sha256(f"{prefix}{r['id']}".encode("ascii")).digest()
    )
    held = ordered[: math.ceil(len(rows) / 4)]
    results = {}
    for key, model in frozen["models"].items():
        ll = []
        for r in held:
            x = [1, (r["age_years"] - 35) / 10, r["source_male"], r["tr360"] - 1.5, r["ambulatory"]]
            mu = np.dot(x[: len(model["coefficients"])], model["coefficients"])
            lo = (math.log(r["left_h"]) - mu) / model["scale"] if r["left_h"] else -math.inf
            log_probability = log_expit(-lo)
            if r["right_h"] is not None:
                hi = (math.log(r["right_h"]) - mu) / model["scale"]
                log_probability += log_expit(hi) + np.log(-np.expm1(lo - hi))
            ll.append(log_probability)
        results[key] = float(-np.mean(ll))
        if not math.isclose(
            results[key], frozen["evaluation"]["held_out_nll_per_observation"][key], abs_tol=1e-8
        ):
            raise ValueError("Public Grade IV interval likelihood differs from its frozen result")
    return {"endpoint": "grade_iv_vge", "held_out_ids": len(held), "interval_nll": results}


def assess_external(r, model):
    """Compare one published group's pre-exposure information to the locked NASA estimand."""
    reasons = []
    if r["population_scope"] != "nasa_chamber_research":
        reasons.append("population_outside_reference")
    if r["endpoint"] != "dcs":
        reasons.append("endpoint_is_" + r["endpoint"])
    if r["window_code"] != "nasa_test_ascertainment":
        reasons.append("ascertainment_" + r["window_code"])
    if r["denominator_unit"] != "exposures":
        reasons.append("denominator_unit_unresolved")
    if not r["single_protocol"]:
        reasons.append("mixed_protocols")
    if r["plateau_min"] is None:
        reasons.append("plateau_duration_unavailable")
    elif not 120 <= r["plateau_min"] <= 360:
        reasons.append("plateau_duration_outside_support")
    for field in ("body_pressure_psia", "mean_tr360", "ambulatory"):
        if r[field] is None:
            reasons.append(field + "_unavailable")
    point = None
    if not reasons:
        point, _ = group_estimate(
            model,
            r["body_pressure_psia"],
            r["plateau_min"] / 60,
            r["mean_tr360"],
            bool(r["ambulatory"]),
        )
        if point is None:
            reasons.append("joint_protocol_outside_frozen_support")
    n, y = r["denominator"], r["cases"]
    result = {
        "source": r["source_id"],
        "stratum": r["stratum"],
        "endpoint": r["endpoint"],
        "cases": y,
        "denominator": n,
        "unit": r["denominator_unit"],
        "observed_fraction_of_reported_denominator": y / n,
        "status": "outside_frozen_estimand" if reasons else "scored",
        "reasons": reasons,
        "expected": None,
        "observed_to_expected": None,
        "brier": None,
        "log_loss": None,
        "calibration_intercept": None,
        "calibration_slope": None,
    }
    if point is not None:
        metrics = scores(np.array([n]), np.array([y]), np.array([point]))
        for field in ("expected", "observed_to_expected", "brier", "log_loss"):
            result[field] = metrics[field]
    return result


def run():
    db = sqlite3.connect(":memory:")
    try:
        db.row_factory = sqlite3.Row
        design = populate(db)
        frozen = read_study(GROUP)
        locked = [
            assess_external(r, frozen)
            for r in db.execute("SELECT * FROM locked_external ORDER BY source_id,stratum")
        ]
        return {
            "release": design["release"],
            "software": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
                "sqlite": sqlite3.sqlite_version,
            },
            "manifest_sha256": sha256(DATA / "manifest.json"),
            "design_sha256": sha256(DATA / "design.json"),
            "external_model": design["external_model"],
            "frozen_models": design["frozen_models"],
            "external_evaluation": locked,
            "nasa_family_baseline": nasa_study(db),
            "afrl_activity": afrl_study(db),
            "vge_likelihood_reproduction": vge_check(db),
            "clinical_survival_fit": None,
            "external_recalibration": None,
            "individual_prediction_release": False,
        }
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT.with_name("evaluation.json"))
    args = parser.parse_args()
    content = json.dumps(run(), indent=2, allow_nan=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as folder:
        temp = Path(folder) / "evaluation.json"
        temp.write_text(content, encoding="utf-8", newline="\n")
        publish(temp, args.output)
    print(args.output)
