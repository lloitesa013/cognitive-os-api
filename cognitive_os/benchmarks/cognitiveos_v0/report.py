"""Report helpers for CognitiveOS-v0 benchmark runs."""

from __future__ import annotations

from typing import Any, Dict


def render_markdown(metrics: Dict[str, Any]) -> str:
    lines = [
        "# CognitiveOS-v0 Benchmark Report",
        "",
        f"- Gate Accuracy: {metrics['gate_accuracy']:.2%}",
        f"- Gate Difference Rate: {metrics['gate_difference_rate']:.2%}",
        f"- Profile Separation Score: {metrics['profile_separation_score']:.2%}",
        f"- Trace Completeness: {metrics['trace_completeness']:.2%}",
        "",
        "| Scenario | Category | Guardian | Truth First | Progress Max |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in metrics["details"]:
        gates = row["actual_gates"]
        lines.append(
            "| {scenario_id} | {category} | {guardian} | {truth_first} | {progress_max} |".format(
                scenario_id=row["scenario_id"],
                category=row["category"],
                guardian=gates.get("guardian", ""),
                truth_first=gates.get("truth_first", ""),
                progress_max=gates.get("progress_max", ""),
            )
        )
    return "\n".join(lines)
