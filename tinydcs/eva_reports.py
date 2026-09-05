"""Self-contained, source-labelled EVA reports recomputed from validated inputs."""

from __future__ import annotations
import base64
import html
import io
import json
import math
import re
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _fmt(value, digits=2):
    if value is None or isinstance(value, float) and not math.isfinite(value):
        return "Unavailable"
    if isinstance(value, (float, int)):
        return f"{value:.{digits}f}"
    return str(value)


def report_payload(response):
    result = response["result"]
    stamp = datetime.now(timezone.utc)
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", response["scenarioId"])
    return {
        **response,
        "reportId": f"eva-{safe_id}-{stamp.strftime('%Y%m%dT%H%M%SZ')}",
        "generatedAt": stamp.isoformat(),
        "summary": {
            "decision": result["decision"],
            "decisionRationale": result["decisionRationale"],
            "pointRiskPercent": result["pDcsPercent"],
            "intervalLowPercent": None,
            "intervalHighPercent": None,
            "inEnvelope": result["inEnvelope"],
            "abstain": result["abstain"],
            "envelopeWarnings": result["envelopeWarnings"],
            "stopReasons": result["stopReasons"],
        },
        "timeline": result["timeline"],
        "hazards": result["hazards"],
        "disclaimer": "Reference calculations and configured planning rules only. No operational clearance or individual clinical validation is implied.",
    }


def report_json(payload):
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)


def _metrics(payload):
    result = payload["result"]
    probability = _fmt(result["pDcsPercent"]) + ("%" if result["pDcsPercent"] is not None else "")
    return [
        ("NASA reference endpoint", probability),
        ("Interval", "Unavailable — no calibrated EVA interval"),
        ("N2 after prebreathe", _fmt(result["p1n2Psia"]) + " psia (dry convention)"),
        ("ETR at entry", _fmt(result["etr"])),
        ("PLSS margin", _fmt(result["consumablesMarginMin"], 0) + " min"),
        ("Oxygen reserve (separate)", _fmt(result["oxygenReserveMin"], 0) + " min"),
    ]


def _indicator(hazard):
    indicator = hazard.get("indicator")
    if indicator:
        return _fmt(indicator["value"]) + " " + indicator["unit"]
    value = hazard["probabilityPercent"]
    return _fmt(value) + (" % at reference horizon" if value is not None else "")


def report_html(payload):
    escape = html.escape
    result = payload["result"]
    metric_rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>"
        for label, value in _metrics(payload)
    )
    hazard_rows = "".join(
        f"<tr><td>{escape(h['name'])}</td><td>{escape(_indicator(h))}</td><td>{escape(h['driver'])}</td></tr>"
        for h in result["hazards"]
    )
    timeline_rows = "".join(
        f"<tr><td>{_fmt(p['timeMin'])}</td><td>{escape(p['phase'])}</td><td>{_fmt(p['ambientPressurePsia'])}</td><td>{_fmt(p['tissueN2Psia'])}</td><td>{_fmt(p['vo2MlKgMin'])}</td></tr>"
        for p in result["timeline"]
    )
    warnings = "".join(f"<li>{escape(value)}</li>" for value in result["envelopeWarnings"])
    stops = (
        ", ".join(result["stopReasons"])
        or "No configured stop flagged; this does not establish safety."
    )
    metadata = json.dumps(
        payload["modelMetadata"]
        | {
            "applicability": result["modelApplicability"],
            "inputFingerprint": payload.get("inputFingerprint"),
        },
        indent=2,
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EVA DCS Planning Report</title><style>
body{{font:14px/1.5 system-ui,sans-serif;margin:32px;color:#172033;max-width:1100px}}
table{{border-collapse:collapse;width:100%;margin:16px 0}}th,td{{text-align:left;padding:8px;border:1px solid #ccd2dd}}
th{{background:#f0f3f8}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}h2{{margin-top:28px}}@media print{{body{{margin:.5in}}}}
</style></head><body><h1>EVA DCS Planning Report</h1>
<p>Scenario: {escape(payload["scenarioId"])} · Rules: {escape(payload["missionRuleProfile"])}</p>
<h2>Planning classification: {escape(result["decision"])}</h2><p>{escape(result["decisionRationale"])}</p>
<p>Stop conditions: {escape(stops)}</p><table>{metric_rows}</table>
<h2>Applicability</h2><ul>{warnings}</ul><p>No cumulative-risk trajectory or EVA confidence interval is available from the endpoint regression.</p>
<h2>Indicators, not event probabilities</h2><table><tr><th>Indicator</th><th>Value</th><th>Interpretation</th></tr>{hazard_rows}</table>
<h2>Sequential nitrogen calculation</h2><p>Single-compartment model extension; dry ambient N2. VO2 is declared total oxygen consumption.</p>
<table><tr><th>Time min</th><th>Phase</th><th>Pressure psia</th><th>Tissue N2 psia</th><th>VO2 mL/kg/min</th></tr>{timeline_rows}</table>
<h2>Source and input metadata</h2><pre>{escape(metadata)}</pre><p>{escape(payload["disclaimer"])}</p></body></html>"""


def report_pdf_base64(payload):
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    result = payload["result"]
    paragraph = lambda value: Paragraph(html.escape(str(value)), styles["BodyText"])
    story = [
        Paragraph("EVA DCS Planning Report", styles["Title"]),
        paragraph(f"Scenario: {payload['scenarioId']} | Rules: {payload['missionRuleProfile']}"),
        paragraph(f"Planning classification: {result['decision']}"),
        paragraph(result["decisionRationale"]),
        Spacer(1, 0.15 * inch),
    ]
    table = Table(
        [[paragraph(k), paragraph(v)] for k, v in _metrics(payload)],
        colWidths=[2.1 * inch, 4.3 * inch],
    )
    table.setStyle(
        TableStyle(
            [("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 0.15 * inch),
            Paragraph("Applicability and stop conditions", styles["Heading2"]),
        ]
    )
    for text in result["stopReasons"] + result["envelopeWarnings"]:
        story.append(paragraph(text))
    story.append(Paragraph("Indicators (no calibrated event probabilities)", styles["Heading2"]))
    for hazard in result["hazards"]:
        story.append(
            paragraph(hazard["name"] + ": " + _indicator(hazard) + ". " + hazard["driver"])
        )
    story.extend(
        [
            Spacer(1, 0.15 * inch),
            paragraph("Model: " + payload["modelMetadata"]["modelVersion"]),
            paragraph("Source: " + result["modelApplicability"]["source"]),
            paragraph(payload["disclaimer"]),
        ]
    )
    SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5 * inch, leftMargin=0.5 * inch).build(
        story
    )
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def report_artifacts(response):
    payload = report_payload(response)
    name = payload["reportId"]
    return {
        "reportId": name,
        "generatedAt": payload["generatedAt"],
        "artifacts": {
            "json": {
                "filename": name + ".json",
                "mimeType": "application/json",
                "content": report_json(payload),
            },
            "html": {
                "filename": name + ".html",
                "mimeType": "text/html",
                "content": report_html(payload),
            },
            "pdf": {
                "filename": name + ".pdf",
                "mimeType": "application/pdf",
                "contentBase64": report_pdf_base64(payload),
            },
        },
    }
