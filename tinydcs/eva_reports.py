"""Exportable EVA planning report artifacts."""

from __future__ import annotations

import base64
import html
import io
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _fmt(value: Any, digits: int = 2) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def report_payload(response: Mapping[str, Any]) -> dict[str, Any]:
    result = response["result"]
    return {
        "reportId": f"eva-{response['scenarioId']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "scenarioId": response["scenarioId"],
        "missionRuleProfile": response["missionRuleProfile"],
        "modelMetadata": response["modelMetadata"],
        "summary": {
            "decision": result["decision"],
            "decisionRationale": result["decisionRationale"],
            "pointRiskPercent": result["pDcsPercent"],
            "intervalLowPercent": result["intervalLowPercent"],
            "intervalHighPercent": result["intervalHighPercent"],
            "maxRiskPercent": result["maxRiskPercent"],
            "maxRiskTimeMin": result["maxRiskTimeMin"],
            "integratedRiskPercentHours": result["integratedRiskPercentHours"],
            "lxcLikelihood": result["lxcLikelihood"],
            "lxcConsequence": result["lxcConsequence"],
            "lxcScore": result["lxcScore"],
            "lxcCategory": result["lxcCategory"],
            "inEnvelope": result["inEnvelope"],
            "abstain": result["abstain"],
            "envelopeWarnings": result["envelopeWarnings"],
            "telemetryStatus": result.get("telemetryStatus", {}),
        },
        "timeline": result["timeline"],
        "hazards": result["hazards"],
        "disclaimer": (
            "Research and planning artifact only. Not certified flight software, "
            "not clinical software, and not a sole source for operational decisions."
        ),
    }


def report_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def report_html(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    warnings = "".join(f"<li>{html.escape(warning)}</li>" for warning in summary["envelopeWarnings"])
    hazards = "".join(
        "<tr>"
        f"<td>{html.escape(h['name'])}</td>"
        f"<td>{_fmt(h['probabilityPercent'])}%</td>"
        f"<td>{h['likelihood']} x {h['consequence']} = {h['score']}</td>"
        f"<td>{html.escape(h['posture'])}</td>"
        f"<td>{html.escape(h['driver'])}</td>"
        "</tr>"
        for h in payload["hazards"]
    )
    timeline = "".join(
        "<tr>"
        f"<td>{_fmt(p['timeMin'], 0)}</td>"
        f"<td>{html.escape(p['phase'])}</td>"
        f"<td>{_fmt(p['ambientPressurePsia'])}</td>"
        f"<td>{_fmt(p['tissueN2Psia'])}</td>"
        f"<td>{_fmt(p['cumulativePDcsPercent'])}%</td>"
        f"<td>{_fmt(p['intervalLowPercent'])}-{_fmt(p['intervalHighPercent'])}%</td>"
        "</tr>"
        for p in payload["timeline"][:: max(1, len(payload["timeline"]) // 12)]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(payload['reportId'])}</title>
  <style>
    body {{ font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; margin: 36px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ font-size: 26px; }}
    h2 {{ font-size: 17px; margin-top: 28px; border-top: 1px solid #d1d5db; padding-top: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 16px 0; }}
    .metric {{ border: 1px solid #d1d5db; padding: 10px; border-radius: 6px; }}
    .metric strong {{ display: block; font-size: 20px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 7px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .decision {{ display: inline-block; padding: 4px 8px; border: 1px solid #9ca3af; border-radius: 999px; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; }}
    .disclaimer {{ margin-top: 28px; font-size: 12px; color: #4b5563; }}
    @media print {{ body {{ margin: .55in; }} }}
  </style>
</head>
<body>
  <h1>EVA DCS Planning Report</h1>
  <p><span class="decision">{html.escape(summary['decision'])}</span> {html.escape(summary['decisionRationale'])}</p>
  <p><strong>Scenario:</strong> {html.escape(payload['scenarioId'])} &nbsp; <strong>Mission rules:</strong> {html.escape(payload['missionRuleProfile'])}</p>
  <div class="grid">
    <div class="metric">Point risk<strong>{_fmt(summary['pointRiskPercent'])}%</strong></div>
    <div class="metric">95% interval<strong>{_fmt(summary['intervalLowPercent'])}-{_fmt(summary['intervalHighPercent'])}%</strong></div>
    <div class="metric">Max risk<strong>{_fmt(summary['maxRiskPercent'])}% @ T+{_fmt(summary['maxRiskTimeMin'], 0)}m</strong></div>
    <div class="metric">LxC<strong>{summary['lxcLikelihood']} x {summary['lxcConsequence']} = {summary['lxcScore']}</strong></div>
  </div>
  <h2>Envelope</h2>
  <p>{'In envelope' if summary['inEnvelope'] else 'Abstain / out of envelope'}</p>
  <ul>{warnings or '<li>No envelope warnings.</li>'}</ul>
  <h2>Hazard Matrix Rows</h2>
  <table><thead><tr><th>Hazard</th><th>Probability</th><th>LxC</th><th>Posture</th><th>Driver</th></tr></thead><tbody>{hazards}</tbody></table>
  <h2>Risk Trajectory Sample</h2>
  <table><thead><tr><th>Time min</th><th>Phase</th><th>Ambient psia</th><th>Tissue N2 psia</th><th>P(DCS)</th><th>95% interval</th></tr></thead><tbody>{timeline}</tbody></table>
  <h2>Model Metadata</h2>
  <pre>{html.escape(json.dumps(payload['modelMetadata'], indent=2))}</pre>
  <p class="disclaimer">{html.escape(payload['disclaimer'])}</p>
</body>
</html>"""


def report_pdf_base64(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5 * inch, leftMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    story: list[Any] = [
        Paragraph("EVA DCS Planning Report", styles["Title"]),
        Paragraph(f"Decision: <b>{html.escape(summary['decision'])}</b>", styles["Heading2"]),
        Paragraph(html.escape(summary["decisionRationale"]), styles["BodyText"]),
        Spacer(1, 0.12 * inch),
    ]
    metrics = [
        ["Scenario", payload["scenarioId"]],
        ["Mission rules", payload["missionRuleProfile"]],
        ["Point risk", f"{_fmt(summary['pointRiskPercent'])}%"],
        ["95% interval", f"{_fmt(summary['intervalLowPercent'])}-{_fmt(summary['intervalHighPercent'])}%"],
        ["Max risk", f"{_fmt(summary['maxRiskPercent'])}% @ T+{_fmt(summary['maxRiskTimeMin'], 0)}m"],
        ["Integrated risk", f"{_fmt(summary['integratedRiskPercentHours'])} %-h"],
        ["LxC", f"{summary['lxcLikelihood']} x {summary['lxcConsequence']} = {summary['lxcScore']}"],
        ["Envelope", "in" if summary["inEnvelope"] else "abstain"],
    ]
    table = Table(metrics, colWidths=[1.7 * inch, 4.8 * inch])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke)]))
    story.extend([table, Spacer(1, 0.16 * inch), Paragraph("Hazards", styles["Heading2"])])
    hazard_rows = [["Hazard", "Probability", "LxC", "Posture"]]
    hazard_rows.extend(
        [h["name"], f"{_fmt(h['probabilityPercent'])}%", f"{h['likelihood']} x {h['consequence']} = {h['score']}", h["posture"]]
        for h in payload["hazards"]
    )
    hazard_table = Table(hazard_rows, colWidths=[2.0 * inch, 1.3 * inch, 1.4 * inch, 1.1 * inch])
    hazard_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke)]))
    story.extend([hazard_table, Spacer(1, 0.16 * inch)])
    if summary["envelopeWarnings"]:
        story.append(Paragraph("Envelope Warnings", styles["Heading2"]))
        for warning in summary["envelopeWarnings"]:
            story.append(Paragraph(f"- {html.escape(warning)}", styles["BodyText"]))
    story.extend([Spacer(1, 0.16 * inch), Paragraph(html.escape(payload["disclaimer"]), styles["BodyText"])])
    doc.build(story)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def report_artifacts(response: Mapping[str, Any]) -> dict[str, Any]:
    payload = report_payload(response)
    filename_base = payload["reportId"]
    return {
        "reportId": payload["reportId"],
        "generatedAt": payload["generatedAt"],
        "artifacts": {
            "json": {
                "filename": f"{filename_base}.json",
                "mimeType": "application/json",
                "content": report_json(payload),
            },
            "html": {
                "filename": f"{filename_base}.html",
                "mimeType": "text/html",
                "content": report_html(payload),
            },
            "pdf": {
                "filename": f"{filename_base}.pdf",
                "mimeType": "application/pdf",
                "contentBase64": report_pdf_base64(payload),
            },
        },
    }
