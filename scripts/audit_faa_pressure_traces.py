"""Summarize pressure-channel coverage in the public FAA OFOS SmartLab ZIP."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile


def clock_ms(value):
    hours, minutes, seconds = value.split(":")
    return (int(hours) * 60 + int(minutes)) * 60_000 + round(float(seconds) * 1000)


def trace_statistics(stream):
    for _ in range(5):
        next(stream)
    names, units = [next(csv.reader([next(stream)])) for _ in range(2)]
    if (
        (names[0], units[0]) != ("Session Time", "sec")
        or (names[28], units[28]) != ("Module 4: Abs. Pressure", "psi")
        or (names[29], units[29]) != ("Module 4: Altitude", "ft")
    ):
        raise ValueError("Unexpected SmartLab pressure channel names or units")

    samples = invalid = nonincreasing = gaps = 0
    first = previous = None
    lowest_pressure = math.inf
    peak_altitude = -math.inf
    for line in stream:
        if not line.strip():
            continue
        fields = line.split(",", 30)
        samples += 1
        try:
            stamp = clock_ms(fields[0])
            pressure, altitude = float(fields[28]), float(fields[29])
            if not (pressure > 0 and math.isfinite(pressure) and math.isfinite(altitude)):
                raise ValueError("Unusable pressure or altitude")
        except (ValueError, OverflowError, IndexError):
            invalid += 1
            continue
        if previous is None:
            first = stamp
        else:
            nonincreasing += stamp <= previous
            gaps += stamp - previous > 100
        previous = stamp
        lowest_pressure = min(lowest_pressure, pressure)
        peak_altitude = max(peak_altitude, altitude)
    if first is None or previous <= first:
        raise ValueError("No valid SmartLab logging span")
    return samples, invalid, nonincreasing, gaps, (previous - first) / 1000, lowest_pressure, peak_altitude


def audit(archive):
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    traces = []
    with ZipFile(archive) as outer:
        for member in outer.infolist():
            if member.is_dir():
                continue
            with ZipFile(io.BytesIO(outer.read(member))) as inner:
                trace, = [m for m in inner.infolist() if not m.is_dir()]
                with io.TextIOWrapper(inner.open(trace), encoding="utf-8-sig", newline="") as stream:
                    traces.append(trace_statistics(stream))
    counts, invalid, nonincreasing, gaps, spans, pressures, peaks = zip(*traces, strict=True)
    return {
        "archive_sha256": digest,
        "files_checked": len(traces),
        "sample_count": sum(counts),
        "invalid_samples": sum(invalid),
        "nonincreasing_clock_intervals": sum(nonincreasing),
        "recorded_gaps_gt_0_1s": sum(gaps),
        "files_with_altitude_at_least_44000_ft": sum(peak >= 44_000 for peak in peaks),
        "shortest_logged_seconds": min(spans),
        "longest_logged_seconds": max(spans),
        "lowest_absolute_pressure_psi": min(pressures),
        "lowest_trace_peak_altitude_ft": min(peaks),
        "highest_trace_peak_altitude_ft": max(peaks),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    print(json.dumps(audit(parser.parse_args().archive), indent=2))
