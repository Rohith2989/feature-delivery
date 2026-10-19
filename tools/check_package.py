#!/usr/bin/env python3
"""Validate the distributable's local links and core metadata; no network calls."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path) -> list[str]:
    errors: list[str] = []
    skill = root / "skills" / "feature-delivery"
    try:
        metadata = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
        if metadata.get("name") != skill.name or not re.fullmatch(
            r"\d+\.\d+\.\d+", str(metadata.get("version", ""))
        ):
            errors.append("plugin name/version must match the skill package")
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        front = text.split("---", 2)
        if len(front) != 3 or front[0].strip():
            errors.append("SKILL.md must start with frontmatter")
        elif not re.search(r"^name: feature-delivery$", front[1], re.M) or not re.search(
            r"^description: .+", front[1], re.M
        ):
            errors.append("skill discovery metadata missing")
        if "[TODO:" in text:
            errors.append("unfinished skill scaffold")
    except (OSError, ValueError) as exc:
        errors.append(f"missing or invalid core metadata: {exc}")

    # Only real Markdown links, not template placeholders or external destinations.
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        for raw in re.findall(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)", path.read_text(encoding="utf-8")):
            target = raw.strip().split(' "', 1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f"{path.relative_to(root)}: missing or escaping link {target}")
    return errors


def main() -> int:
    errors = check(ROOT)
    if errors:
        print("Package check failed:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print("Package metadata and local Markdown links checked; no network/host compatibility claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
