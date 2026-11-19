"""Descriptive break timing, separate from probability and operational conformance."""
from tinydcs.exposure import SECONDS_PER_UNIT, ExposureProfile

SOURCE = "https://ntrs.nasa.gov/citations/20240016139"


def interruption_record(profile: ExposureProfile) -> dict:
    segments = profile.segments
    scale = SECONDS_PER_UNIT[profile.time_unit]
    events = []
    nitrogen_minutes = 0.0
    unknown_gas = False
    for i, s in enumerate(segments):
        kind = s.break_kind
        if kind is None:
            kind = {"oxygen_break": "breathing_gas", "purge": "purge"}.get(s.phase)
        if kind is None:
            continue
        minutes = profile.minutes(s)
        end_gas = s.end_gas or s.gas
        next_gas = segments[i+1].gas if i+1 < len(segments) else None
        if kind in {"breathing_gas", "mask_to_suit"}:
            if s.gas is None:
                unknown_gas = True
            elif any(g.nitrogen_fraction + g.argon_fraction > 0 for g in (s.gas, end_gas)):
                # A linear ramp with nitrogen at either end contains nitrogen
                # for the interval, except possibly at a single endpoint.
                nitrogen_minutes += minutes
        events.append({
            "segment_id": s.id, "kind": kind, "duration_minutes": minutes,
            "start_seconds": s.start*scale, "end_seconds": s.end*scale,
            "start_pressure_pa": s.start_pressure.pascals(), "end_pressure_pa": s.end_pressure.pascals(),
            "inspired_oxygen_fraction": s.gas.oxygen_fraction if s.gas else None,
            "end_oxygen_fraction": end_gas.oxygen_fraction if end_gas else None,
            "start_nitrogen_fraction": s.gas.nitrogen_fraction if s.gas else None,
            "end_nitrogen_fraction": end_gas.nitrogen_fraction if end_gas else None,
            "next_oxygen_fraction": next_gas.oxygen_fraction if next_gas else None,
            "previous_delivery": segments[i-1].gas.delivery_method if i and segments[i-1].gas else None,
            "next_delivery": next_gas.delivery_method if next_gas else None,
        })
    return {
        "status": "not_evaluated", "reason": "CONTROLLED_PROCEDURE_NOT_VERIFIED",
        "source": SOURCE, "authority": "NASA", "source_document": "NASA/TP-20240016139",
        "publication_date": "2024-10", "reported_implementation": "2023-09",
        "protocol": "ISS ISLE Phase 3, historical source context",
        "events": events,
        "documented_nitrogen_break_minutes": None if unknown_gas else nitrogen_minutes,
        "operational_cumulative_break_minutes": None,
        "boundary_note": "Section 6.1 uses <10 minutes and the consolidated Section 6.2 table uses ≤10 minutes.",
    }
