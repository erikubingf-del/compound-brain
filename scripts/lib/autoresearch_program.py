from __future__ import annotations

from pathlib import Path


SECTION_MAP = {
    "objective": "objective",
    "mutable surfaces": "mutable_surfaces",
    "protected surfaces": "protected_surfaces",
    "fixed evaluator": "fixed_evaluator",
    "run command": "run_command",
    "metric extraction rule": "metric_extraction_rule",
    "keep/discard rule": "keep_discard_rule",
    "runtime budget": "runtime_budget",
    "repair cap": "repair_cap",
    "max iterations": "max_iterations",
}


def load_autoresearch_program(program_path: Path) -> dict[str, object]:
    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for raw_line in program_path.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            heading = line[3:].strip().lower()
            current_key = SECTION_MAP.get(heading)
            if current_key:
                sections[current_key] = []
            continue
        if current_key:
            sections[current_key].append(raw_line.rstrip())

    def parse_list(key: str) -> list[str]:
        values = []
        for line in sections.get(key, []):
            stripped = line.strip()
            if stripped.startswith("- "):
                values.append(stripped[2:].strip())
        return values

    def parse_text(key: str) -> str:
        for line in sections.get(key, []):
            stripped = line.strip()
            if stripped:
                return stripped
        return ""

    return {
        "objective": parse_text("objective"),
        "mutable_surfaces": parse_list("mutable_surfaces"),
        "protected_surfaces": parse_list("protected_surfaces"),
        "fixed_evaluator": parse_text("fixed_evaluator"),
        "run_command": parse_text("run_command"),
        "metric_extraction_rule": parse_text("metric_extraction_rule"),
        "keep_discard_rule": parse_text("keep_discard_rule"),
        "runtime_budget": parse_text("runtime_budget"),
        "repair_cap": parse_text("repair_cap"),
        "max_iterations": parse_text("max_iterations"),
    }
