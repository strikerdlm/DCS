#!/usr/bin/env python3
"""Audit and clean ``DCS_Risk_DB_2025.csv``.

Usage
-----
    python scripts/01_clean_data.py \
        --input ../Model_Rel_Candidate/DCS_Risk_DB_2025.csv \
        --output artifacts/DCS_Risk_DB_2025_clean.parquet \
        --report artifacts/data_quality_report.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

# Make the tinydcs package importable when running this script directly.
_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tinydcs.data_clean import run_file


@click.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "output_path", required=True, type=click.Path(dir_okay=False))
@click.option("--report", "report_path", required=True, type=click.Path(dir_okay=False))
def main(input_path: str, output_path: str, report_path: str) -> None:
    report = run_file(Path(input_path), Path(output_path), Path(report_path))
    click.echo(
        "Cleaned {n_in} → {n_out} rows. "
        "Rescaled fraction→percent: {n_fix}. "
        "Cells with disagreement: {n_dis}. "
        "Rows removed by dedup: {n_ded}.".format(
            n_in=report.n_rows_in,
            n_out=report.n_rows_out,
            n_fix=report.n_scale_fixed,
            n_dis=report.n_within_combo_disagreements,
            n_ded=report.n_rows_deduped,
        )
    )


if __name__ == "__main__":
    main()
