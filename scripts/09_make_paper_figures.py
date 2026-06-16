#!/usr/bin/env python3
"""Generate the TinyDCS figure set.

Reads the artifacts produced by scripts/01, /04, /06, /08 and emits a
self-contained figure bundle at publication resolution (PNG at 300 DPI + PDF
for vector inclusion). Figures use compact single-column and double-column
layouts with sans-serif text readable at 8-point body text.

Figures produced
----------------
    fig1_reliability_diagram.{png,pdf}
        Reliability (calibration) diagram for TinyDCS vs the ADRAC
        closed-form baseline on the random-split test fold.
    fig2_per_band_coverage.{png,pdf}
        Empirical 95% coverage of the zero-inflated conformal interval
        stratified by 5,000-ft altitude band; compares the five calibration
        strategies reported in §3.5 of the draft manuscript.
    fig3_size_vs_accuracy.{png,pdf}
        ONNX footprint vs test-set MAE for the four size variants
        (full / medium / compact / tiny).
    fig4_personalization_info_gain.{png,pdf}
        Hierarchical Bayesian personalization: Pearson r of log-λ recovery
        and population-vs-personalized Brier score as a function of per-
        subject exposures k (Paper 2 prototype, synthetic cohort).
    fig5_architecture.{png,pdf}
        Three-layer block diagram (mechanistic → ML surrogate → fusion /
        personalization) rendered in matplotlib.

Usage
-----
    python scripts/09_make_paper_figures.py \\
        --metrics-zi artifacts/metrics_adrac_zi.json \\
        --metrics-cqr artifacts/metrics_adrac_cqr.json \\
        --metrics-mcqr artifacts/metrics_adrac_mcqr.json \\
        --metrics-v0p3 artifacts/metrics_adrac_v0.3.json \\
        --metrics-v0p4 artifacts/metrics_adrac_v0.4.json \\
        --size-ladder artifacts/compact_vs_full.json \\
        --personalization artifacts/personalization_demo.json \\
        --surrogate artifacts/tinydcs_adrac_zi.joblib \\
        --training artifacts/DCS_Risk_DB_2025_clean.parquet \\
        --output-dir artifacts/paper_figures

The script is additive: any artifact that is missing is skipped with a
warning, the corresponding figure is omitted, and the remaining figures
are still produced. This matters when a downstream agent wants to rebuild
just (say) the personalization figure without re-running the full training
pipeline.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import click
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ---------------------------------------------------------------- style

def _apply_style() -> None:
    """Readable 8-point, sans-serif, tight-grid figure style."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": ":",
    })


def _save(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{stem}.png")
    fig.savefig(out_dir / f"{stem}.pdf")
    plt.close(fig)


def _load_json(path: str | None) -> dict | None:
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        click.echo(f"  [skip] {path} not found", err=True)
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# -------------------------------------------------- Fig 1: reliability

def _reliability_bins_from_predictions(y_true: np.ndarray, y_pred: np.ndarray, n_bins: int = 10) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute binned predicted-vs-observed means and bin sizes."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.clip(np.asarray(y_pred, dtype=float), 0.0, 1.0)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(y_pred, edges[1:-1]), 0, n_bins - 1)
    pred_mean = np.zeros(n_bins)
    obs_mean = np.zeros(n_bins)
    counts = np.zeros(n_bins, dtype=int)
    for b in range(n_bins):
        m = idx == b
        counts[b] = int(m.sum())
        if counts[b] > 0:
            pred_mean[b] = float(y_pred[m].mean())
            obs_mean[b] = float(y_true[m].mean())
    return pred_mean, obs_mean, counts


def _fig1_reliability(
    out_dir: Path,
    surrogate_path: str | None,
    training_path: str | None,
) -> None:
    if surrogate_path is None or training_path is None:
        click.echo("  [skip] fig1 needs --surrogate + --training")
        return
    from tinydcs.surrogate import TinyDcsSurrogate
    from tinydcs.features import FEATURE_COLUMNS
    from tinydcs.simulator import ExposureProfile, ornstein_uhlenbeck_vo2
    from tinydcs.features import extract_features as _ef

    click.echo("  [fig1] rebuilding features on the clean grid + predicting ...")
    surrogate = TinyDcsSurrogate.load(surrogate_path)
    df = pd.read_parquet(training_path)

    VO2 = {"Rest": (0.10, 0.05), "Mild": (0.45, 0.10), "Heavy": (1.10, 0.15)}
    rng = np.random.default_rng(42)
    feat_rows, y = [], []
    for _, row in df.iterrows():
        m, sd = VO2.get(str(row["exercise_level"]), VO2["Rest"])
        mm = max(0.0, rng.normal(m, sd))
        t = float(row["time_at_altitude"])
        traj = ornstein_uhlenbeck_vo2(duration_min=t, dt_min=5.0, mean_i_ex=mm, rng=rng)
        p = ExposureProfile(
            target_altitude_ft=float(row["altitude"]),
            prebreathe_duration_min=float(row["prebreathing_time"]),
            prebreathe_fio2=1.0, prebreathe_fin2=0.0,
            prebreathe_i_ex_trajectory=0.0, ascent_rate_fpm=5000.0,
            altitude_duration_min=t, altitude_fio2=0.21, altitude_fin2=0.79,
            altitude_i_ex_trajectory=traj, vo2_dt_min=5.0,
        )
        feat_rows.append(asdict(_ef(p)))
        y.append(float(row["risk_of_decompression_sickness"]) / 100.0)

    X = pd.DataFrame(feat_rows)[list(FEATURE_COLUMNS)]
    y = np.asarray(y)
    rng2 = np.random.default_rng(7)
    test_mask = rng2.random(len(y)) < 0.15
    X_test, y_test = X[test_mask], y[test_mask]
    preds = surrogate.predict(X_test)
    y_hat = np.asarray(preds["point"])

    fig, ax = plt.subplots(figsize=(3.3, 3.3))
    pm, om, cnt = _reliability_bins_from_predictions(y_test, y_hat, n_bins=10)
    m = cnt > 0
    ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="Ideal")
    ax.scatter(pm[m], om[m], s=np.sqrt(cnt[m]) * 3.0, color="#C44E52", alpha=0.85, edgecolor="k", linewidth=0.4, label="TinyDCS (zero-inflated)")
    for i in np.where(m)[0]:
        ax.annotate(f"n={cnt[i]}", xy=(pm[i], om[i]), xytext=(3, -3), textcoords="offset points", fontsize=6, color="#555")
    ax.set_xlabel("Predicted P(DCS)")
    ax.set_ylabel("Observed P(DCS)")
    ax.set_title("Reliability diagram (test fold)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal", "box")
    ax.legend(loc="upper left", frameon=False)
    _save(fig, out_dir, "fig1_reliability_diagram")


# ----------------------------------------- Fig 2: per-band coverage

def _fig2_per_band_coverage(
    out_dir: Path,
    metrics_map: dict[str, dict | None],
) -> None:
    """Grouped bar chart: per-band coverage across five calibration modes."""
    labels_order = ["Global conformal", "Mondrian", "CQR (global)", "Mondrian-CQR", "Zero-inflated"]
    source_keys = ["v0p3", "v0p4", "cqr", "mcqr", "zi"]
    band_keys = ["18000-23000_ft", "23000-28000_ft", "28000-33000_ft", "33000-38000_ft", "38000-43000_ft"]
    band_labels = ["18–23K", "23–28K", "28–33K", "33–38K", "38–43K"]

    coverages = {}
    for lab, src in zip(labels_order, source_keys):
        m = metrics_map.get(src)
        if m is None:
            click.echo(f"  [skip] fig2 band row: {lab} (no metrics)")
            continue
        band_data = m.get("tinydcs_random_test", {}).get("per_band_coverage", {})
        if not band_data:
            click.echo(f"  [skip] fig2 band row: {lab} (no per_band_coverage)")
            continue
        coverages[lab] = [float(band_data.get(k, {}).get("coverage", np.nan)) for k in band_keys]

    if not coverages:
        click.echo("  [skip] fig2 — no per-band data found")
        return

    fig, ax = plt.subplots(figsize=(6.8, 3.3))
    n_modes = len(coverages)
    width = 0.8 / n_modes
    x = np.arange(len(band_labels))
    colors = ["#4C72B0", "#55A868", "#8172B2", "#CCB974", "#C44E52"]
    for i, (lab, vals) in enumerate(coverages.items()):
        ax.bar(x + (i - (n_modes - 1) / 2) * width, vals, width, label=lab, color=colors[i % len(colors)])
    ax.axhline(0.95, color="k", lw=0.8, ls="--", alpha=0.6)
    ax.text(len(band_labels) - 0.1, 0.952, "nominal = 0.95", fontsize=7, ha="right", va="bottom", color="k")
    ax.set_xticks(x)
    ax.set_xticklabels(band_labels)
    ax.set_xlabel("Altitude band (ft)")
    ax.set_ylabel("Empirical coverage")
    ax.set_title("Per-band conformal coverage, five calibration modes")
    ax.set_ylim(0.4, 1.02)
    ax.legend(loc="lower right", ncol=3, frameon=False)
    _save(fig, out_dir, "fig2_per_band_coverage")


# ----------------------------------------- Fig 3: size vs accuracy

def _fig3_size_vs_accuracy(out_dir: Path, size_ladder: list | None) -> None:
    if size_ladder is None:
        click.echo("  [skip] fig3 — no --size-ladder JSON")
        return

    tags, mae, r2, size_kb = [], [], [], []
    for row in size_ladder:
        tags.append(str(row["tag"]))
        mae.append(float(row["point"]["mae"]))
        r2.append(float(row["point"]["r2"]))
        size_kb.append(float(row["onnx_size_kb"]))

    fig, ax = plt.subplots(figsize=(3.3, 3.3))
    colors = {"full": "#4C72B0", "medium": "#55A868", "compact": "#C44E52", "tiny": "#8172B2"}
    for tg, mm, sz in zip(tags, mae, size_kb):
        ax.scatter(sz, mm, s=70, color=colors.get(tg, "#777"), edgecolor="k", linewidth=0.5, zorder=3)
        ax.annotate(tg, (sz, mm), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.axhline(0.086, color="#555", ls="--", lw=0.8, alpha=0.7)
    ax.text(min(size_kb) * 1.05, 0.088, "ADRAC baseline MAE = 0.086", fontsize=7, color="#555")
    ax.axvline(100.0, color="#AAA", ls=":", lw=0.8)
    ax.text(105, max(mae), "  100 KB target", fontsize=7, color="#777", ha="left", va="top")
    ax.set_xscale("log")
    ax.set_xlabel("ONNX size (KB, log scale)")
    ax.set_ylabel("MAE on random test fold")
    ax.set_title("Size-vs-accuracy Pareto")
    _save(fig, out_dir, "fig3_size_vs_accuracy")


# -------------------------------- Fig 4: personalization info-gain

def _fig4_personalization(out_dir: Path, personalization: dict | None) -> None:
    if personalization is None:
        click.echo("  [skip] fig4 — no --personalization JSON")
        return
    res = personalization.get("results_by_k", {})
    if not res:
        click.echo("  [skip] fig4 — empty results_by_k")
        return

    ks = sorted(int(k.split("_")[1]) for k in res.keys())
    pearson = [float(res[f"k_{k}"]["pearson_r"]) for k in ks]
    br_pop = [float(res[f"k_{k}"]["brier_population"]) for k in ks]
    br_pers = [float(res[f"k_{k}"]["brier_personalized"]) for k in ks]

    fig, ax = plt.subplots(figsize=(3.3, 3.3))
    ax.plot(ks, pearson, marker="o", color="#4C72B0", lw=1.4, label="Pearson r (log λ recovery)")
    ax.set_xscale("log")
    ax.set_xticks(ks)
    ax.set_xticklabels([str(k) for k in ks])
    ax.set_xlabel("Exposures per subject, k")
    ax.set_ylabel("Pearson r")
    ax.set_title("Personalization information gain")
    ax.set_ylim(0, 1.0)

    ax2 = ax.twinx()
    ax2.plot(ks, br_pop, marker="s", color="#555", ls="--", lw=1.0, label="Brier (population)")
    ax2.plot(ks, br_pers, marker="s", color="#C44E52", lw=1.2, label="Brier (personalized)")
    ax2.set_ylabel("Brier score")
    ax2.grid(False)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="lower right", frameon=False, fontsize=7)
    _save(fig, out_dir, "fig4_personalization_info_gain")


# ----------------------------------------- Fig 5: architecture

def _fig5_architecture(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.8, 3.5))
    ax.set_axis_off()

    def box(x, y, w, h, text, color):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="k", linewidth=1.0))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8, wrap=True)

    # Layer 1 — mechanistic
    ax.text(0.5, 0.95, "Layer 1 — Published mechanistic models", fontsize=9, fontweight="bold", ha="left")
    box(0.5, 0.75, 2.0, 0.15, "ADRAC\n(log-logistic AFT)", "#EAF3FA")
    box(2.7, 0.75, 2.0, 0.15, "Conkin RM/NM\n(Eq. 14/15)", "#EAF3FA")
    box(4.9, 0.75, 2.0, 0.15, "Gerth 3RUT-MBe1\n(bubble ODE)\n[calibration WIP]", "#EAF3FA")

    # Layer 2 — surrogate
    ax.text(0.5, 0.65, "Layer 2 — TinyDCS surrogate (this paper)", fontsize=9, fontweight="bold", ha="left")
    box(0.5, 0.40, 6.4, 0.23,
        "LightGBM · 13 features · Smithson-Verkuilen target · logit transform\n"
        "ZERO-INFLATED 2-STAGE: P(y=0) classifier ✕ continuous regressor on y>0\n"
        "Split-conformal on logit residuals · Mahalanobis OOD abstention",
        "#F4ECE0")

    # Layer 3 — fusion + personalization
    ax.text(0.5, 0.32, "Layer 3 — Personalization + fusion (Paper 2)", fontsize=9, fontweight="bold", ha="left")
    box(0.5, 0.10, 3.1, 0.17, "Hierarchical Bayesian\nper-subject log λ\n(conjugate Gaussian)", "#F1E8F1")
    box(3.8, 0.10, 3.1, 0.17, "Wearable multimodal fusion\nHR, HRV, SpO₂, skin T\n(scaffolding only)", "#F1E8F1")

    # Arrows
    ax.annotate("", xy=(3.7, 0.63), xytext=(3.7, 0.75),
                arrowprops=dict(arrowstyle="->", lw=1.0))
    ax.text(3.75, 0.69, "trains on", fontsize=7, ha="left")

    ax.annotate("", xy=(3.7, 0.29), xytext=(3.7, 0.40),
                arrowprops=dict(arrowstyle="->", lw=1.0))
    ax.text(3.75, 0.34, "refines", fontsize=7, ha="left")

    ax.set_xlim(0, 7.5); ax.set_ylim(0, 1.0)
    ax.set_title("TinyDCS three-layer architecture")
    _save(fig, out_dir, "fig5_architecture")


# ------------------------------------------------------------------- CLI

@click.command()
@click.option("--metrics-zi", type=click.Path(dir_okay=False), default="artifacts/metrics_adrac_zi.json", show_default=True)
@click.option("--metrics-cqr", type=click.Path(dir_okay=False), default="artifacts/metrics_adrac_cqr.json", show_default=True)
@click.option("--metrics-mcqr", type=click.Path(dir_okay=False), default="artifacts/metrics_adrac_mcqr.json", show_default=True)
@click.option("--metrics-v0p3", type=click.Path(dir_okay=False), default="artifacts/metrics_adrac_v0.3.json", show_default=True)
@click.option("--metrics-v0p4", type=click.Path(dir_okay=False), default="artifacts/metrics_adrac_v0.4.json", show_default=True)
@click.option("--size-ladder", type=click.Path(dir_okay=False), default="artifacts/compact_vs_full.json", show_default=True)
@click.option("--personalization", type=click.Path(dir_okay=False), default="artifacts/personalization_demo.json", show_default=True)
@click.option("--surrogate", type=click.Path(dir_okay=False), default="artifacts/tinydcs_adrac_zi.joblib", show_default=True)
@click.option("--training", type=click.Path(dir_okay=False), default="artifacts/DCS_Risk_DB_2025_clean.parquet", show_default=True)
@click.option("--output-dir", type=click.Path(file_okay=False), default="artifacts/paper_figures", show_default=True)
def main(
    metrics_zi: str,
    metrics_cqr: str,
    metrics_mcqr: str,
    metrics_v0p3: str,
    metrics_v0p4: str,
    size_ladder: str,
    personalization: str,
    surrogate: str,
    training: str,
    output_dir: str,
) -> None:
    _apply_style()
    out_dir = Path(output_dir)
    click.echo(f"Writing figures to {out_dir}")

    click.echo("\n[fig1] reliability diagram")
    _fig1_reliability(out_dir, surrogate, training)

    click.echo("\n[fig2] per-band coverage")
    metrics_map = {
        "zi": _load_json(metrics_zi),
        "cqr": _load_json(metrics_cqr),
        "mcqr": _load_json(metrics_mcqr),
        "v0p3": _load_json(metrics_v0p3),
        "v0p4": _load_json(metrics_v0p4),
    }
    _fig2_per_band_coverage(out_dir, metrics_map)

    click.echo("\n[fig3] size vs accuracy")
    _fig3_size_vs_accuracy(out_dir, _load_json(size_ladder))

    click.echo("\n[fig4] personalization info gain")
    _fig4_personalization(out_dir, _load_json(personalization))

    click.echo("\n[fig5] architecture")
    _fig5_architecture(out_dir)

    click.echo(f"\nDone. Figure bundle at {out_dir}")


if __name__ == "__main__":
    main()
