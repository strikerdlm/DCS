"""Coverage of the fixed final workbook curves, from archived predictions and bounds."""

from __future__ import annotations

from collections import defaultdict
from statistics import fmean

from pydantic import Field, model_validator

from tinydcs.label_bundle import LabelInput


class HeldOutLabel(LabelInput):
    profile_id: str = Field(min_length=1)
    label_fraction: float = Field(ge=0, le=1)
    lower: float = Field(ge=0, le=1)
    upper: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.lower > self.upper:
            raise ValueError("The saved interval bounds are reversed.")
        return self


def final_coverage(rows):
    groups = defaultdict(list)
    for raw in rows:
        row = HeldOutLabel.model_validate(
            {key: raw[key] for key in HeldOutLabel.model_fields}
        )
        groups["overall", "All curves"].append(row)
        for dim in ("exercise_level", "altitude_ft", "prebreathing_min"):
            value = getattr(row, dim)
            groups[
                dim, format(value, "g") if isinstance(value, float) else value
            ].append(row)
    strata = []
    for (dim, value), group in groups.items():
        profile_hits = {}
        widths, covered = [], 0
        for point in group:
            key = (point.altitude_ft, point.prebreathing_min, point.exercise_level)
            hit = point.lower <= point.label_fraction <= point.upper
            profile_hits[key] = profile_hits.get(key, True) and hit
            covered += hit
            widths.append(100 * (point.upper - point.lower))
        strata.append(
            dict(
                dimension=dim,
                value=value,
                profiles=len(profile_hits),
                covered_profiles=sum(profile_hits.values()),
                points=len(group),
                covered_points=covered,
                mean_width_pp=fmean(widths),
                min_width_pp=min(widths),
                max_width_pp=max(widths),
            )
        )
    return strata
