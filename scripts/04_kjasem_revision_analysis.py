#!/usr/bin/env python3
"""Run the locked KJAsEM-26-0013 major-revision analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tinydcs.kjasem_revision import run_revision_analysis


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with args.config.open("rb") as handle:
        config = tomllib.load(handle)
    summary = run_revision_analysis(config, args.out)
    random_zi = summary["random_split"]["variants"]["zero_inflated"]
    print(
        "KJAsEM revision analysis complete: "
        f"n={summary['n_source_cells']}, "
        f"MAE={random_zi['point']['mae']:.6f}, "
        f"coverage={random_zi['interval']['coverage']:.4f}, "
        f"mean width={random_zi['interval']['mean_width']:.6f}"
    )


if __name__ == "__main__":
    main()
