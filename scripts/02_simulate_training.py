#!/usr/bin/env python3
"""Generate a training set for TinyDCS by running 3RUT-MBe1 on randomized profiles.

Each profile samples altitude, prebreathe, ascent, at-altitude duration, and an
Ornstein–Uhlenbeck VO2 trajectory at altitude. The final P(DCS) from 3RUT-MBe1
is the target. The feature vector (see ``tinydcs.features.FEATURE_COLUMNS``) is
written alongside for direct use by the surrogate trainer.

Usage
-----
    # Pilot (fast, minutes):
    python scripts/02_simulate_training.py --n-profiles 200 --seed 42 \
        --output artifacts/training_pilot.parquet

    # Full (overnight, embarrassingly parallel):
    python scripts/02_simulate_training.py --n-profiles 20000 --seed 42 \
        --workers 8 --output artifacts/training_full.parquet
"""

from __future__ import annotations

import math
import sys
from dataclasses import asdict
from pathlib import Path

import click
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tinydcs.features import FEATURE_COLUMNS, extract_features
from tinydcs.simulator import (  # noqa: E402
    ExposureProfile,
    ornstein_uhlenbeck_vo2,
    simulate_final_pdcs,
)


def _sample_profile(rng: np.random.Generator) -> ExposureProfile:
    altitude = float(rng.uniform(18_000.0, 40_000.0))
    prebreathe_time = float(rng.choice([0.0, 15.0, 30.0, 45.0, 60.0, 90.0, 120.0, 180.0]))
    prebreathe_fio2 = float(rng.choice([1.0, 0.95, 0.85], p=[0.8, 0.1, 0.1]))
    prebreathe_fin2 = 1.0 - prebreathe_fio2 if prebreathe_fio2 < 1.0 else 0.0
    altitude_time = float(rng.uniform(10.0, 240.0))
    altitude_fio2 = float(rng.choice([0.21, 1.0, 0.95], p=[0.8, 0.15, 0.05]))
    altitude_fin2 = 1.0 - altitude_fio2 if altitude_fio2 < 1.0 else 0.0
    ascent_rate = float(rng.choice([5000.0, 1000.0], p=[0.9, 0.1]))
    vo2_dt = 5.0

    pre_mean_i_ex = float(rng.uniform(0.0, 0.8))
    alt_mean_i_ex = float(rng.uniform(0.0, 0.8))
    pre_traj = ornstein_uhlenbeck_vo2(
        duration_min=prebreathe_time,
        dt_min=vo2_dt,
        mean_i_ex=pre_mean_i_ex,
        rng=rng,
    )
    alt_traj = ornstein_uhlenbeck_vo2(
        duration_min=altitude_time,
        dt_min=vo2_dt,
        mean_i_ex=alt_mean_i_ex,
        rng=rng,
    )

    return ExposureProfile(
        target_altitude_ft=altitude,
        prebreathe_duration_min=prebreathe_time,
        prebreathe_fio2=prebreathe_fio2,
        prebreathe_fin2=prebreathe_fin2,
        prebreathe_i_ex_trajectory=pre_traj,
        ascent_rate_fpm=ascent_rate,
        ascent_fio2=0.21,
        ascent_fin2=0.79,
        altitude_duration_min=altitude_time,
        altitude_fio2=altitude_fio2,
        altitude_fin2=altitude_fin2,
        altitude_i_ex_trajectory=alt_traj,
        vo2_dt_min=vo2_dt,
    )


def _run_one(seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    profile = _sample_profile(rng)
    # 3RUT-MBe1 occasionally overflows on pathological FiO2×altitude combos
    # (upstream numerical stability issue). Catch and mark the row as NaN.
    try:
        pdcs = simulate_final_pdcs(profile, dt_min=0.5)
    except (OverflowError, FloatingPointError, ValueError):
        pdcs = float("nan")
    features = extract_features(profile)
    row = asdict(features)
    row["pdcs_3rut_mbe1"] = float(pdcs)
    row["seed"] = int(seed)
    return row


@click.command()
@click.option("--n-profiles", type=int, default=200, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--workers", type=int, default=1, show_default=True)
@click.option("--output", type=click.Path(dir_okay=False), required=True)
@click.option("--progress/--no-progress", default=True)
def main(n_profiles: int, seed: int, workers: int, output: str, progress: bool) -> None:
    if n_profiles <= 0:
        raise click.BadParameter("--n-profiles must be > 0")
    if workers < 1:
        raise click.BadParameter("--workers must be >= 1")

    seeds = list(range(seed, seed + n_profiles))
    if workers == 1:
        iterator = seeds
        if progress:
            iterator = tqdm(iterator, desc="simulate", total=n_profiles)
        rows = [_run_one(s) for s in iterator]
    else:
        rows = Parallel(n_jobs=workers, backend="loky", verbose=10 if progress else 0)(
            delayed(_run_one)(s) for s in seeds
        )

    df = pd.DataFrame(rows)
    # Order columns: features first, then target, then seed.
    cols = list(FEATURE_COLUMNS) + ["pdcs_3rut_mbe1", "seed"]
    df = df[cols]

    n_before = len(df)
    n_failed = int(df["pdcs_3rut_mbe1"].isna().sum())
    df = df.dropna(subset=["pdcs_3rut_mbe1"]).reset_index(drop=True)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".parquet":
        df.to_parquet(out_path, index=False)
    else:
        df.to_csv(out_path, index=False)

    click.echo(
        "Wrote {n} profiles to {p} (target mean={m:.4f}, median={q:.4f}, "
        "nonzero={nz}/{n}, upstream_failures_dropped={f}/{nb}).".format(
            n=len(df),
            p=out_path,
            m=float(df["pdcs_3rut_mbe1"].mean()),
            q=float(df["pdcs_3rut_mbe1"].median()),
            nz=int((df["pdcs_3rut_mbe1"] > 1e-6).sum()),
            f=n_failed,
            nb=n_before,
        )
    )


if __name__ == "__main__":
    main()
