"""Rendering of a table health check in text, JSON, and Markdown.

The plain text report is the one a person reads in a terminal. The
JSON and Markdown forms carry the same facts in shapes a team can
share in a pull request or a ticket without retyping anything.
"""

import json

from .models import TableHealth
from .planner import build_plan
from .scoring import score_table


def check_table(summary):
    """Score one table and build its plan in one call."""
    score, findings = score_table(summary)
    plan = build_plan(summary, findings)
    return TableHealth(summary=summary, score=score, findings=findings, plan=plan)


def render_health(health):
    """Render one table health check as plain text."""
    lines = [f"{health.summary.name}  score {health.score}"]
    for finding in health.findings:
        lines.append(f"  {finding.message}")
    lines.append(f"Plan for {health.summary.name}")
    for index, step in enumerate(health.plan, start=1):
        lines.append(f"  {index}. {step.action}")
        lines.append(f"     Reason. {step.reason}")
        lines.append(f"     Expected saving. {step.estimated_saving}")
        if not step.ready:
            lines.append(f"     Hold off. {step.hold_reason}")
    return "\n".join(lines)


def render_report(summaries):
    """Render health checks for a list of tables."""
    return "\n\n".join(render_health(check_table(summary)) for summary in summaries)


def health_to_dict(health):
    """Return one health check as plain data that JSON can carry."""
    return {
        "table": health.summary.name,
        "score": health.score,
        "findings": [
            {"code": finding.code, "message": finding.message, "points_lost": finding.points_lost}
            for finding in health.findings
        ],
        "plan": [
            {
                "action": step.action,
                "reason": step.reason,
                "estimated_saving": step.estimated_saving,
                "ready": step.ready,
                "hold_reason": step.hold_reason,
            }
            for step in health.plan
        ],
    }


def render_json(summaries):
    """Render health checks for a list of tables as a JSON document."""
    return json.dumps([health_to_dict(check_table(summary)) for summary in summaries], indent=2)


def render_markdown(summaries):
    """Render health checks for a list of tables as Markdown."""
    blocks = []
    for summary in summaries:
        health = check_table(summary)
        lines = [f"## {health.summary.name} score {health.score}", ""]
        for finding in health.findings:
            lines.append(f"- {finding.message}")
        if health.findings:
            lines.append("")
        lines.append(f"Plan for {health.summary.name}")
        lines.append("")
        for index, step in enumerate(health.plan, start=1):
            lines.append(f"{index}. {step.action}")
            lines.append(f"   Reason. {step.reason}")
            lines.append(f"   Expected saving. {step.estimated_saving}")
            if not step.ready:
                lines.append(f"   Hold off. {step.hold_reason}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
