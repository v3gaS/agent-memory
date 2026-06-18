#!/usr/bin/env python3
"""Register a new subsystem: deep ref stub + AGENTS.md + docs/README.md rows.

Usage:
  python3 scripts/register_subsystem.py \\
    --slug auth \\
    --title "Authentication" \\
    --paths "src/auth/**" \\
    --test "pytest tests/test_auth.py -q" \\
    --never "Never store passwords in plaintext"
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _repo_root() -> Path:
    return Path.cwd()


def _slug_to_doc(slug: str) -> str:
    return f"docs/{slug.upper()}.md"


def _read_template(root: Path) -> str:
    tpl = root / "docs" / "SUBSYSTEM_TEMPLATE.md"
    if not tpl.is_file():
        # fallback minimal stub
        return f"# {{TITLE}} — Full Reference\n\nLast updated: {{DATE}}.\n\n## 1. Overview\n\nTODO\n\n## 20. Changelog\n\n- **{{DATE}}** — Initial stub via register_subsystem.py.\n"
    text = tpl.read_text(encoding="utf-8")
    # Replace generic CORE references with this subsystem title in overview TODO
    return text


def _ensure_doc(root: Path, slug: str, title: str, force: bool) -> Path:
    doc_path = root / _slug_to_doc(slug)
    if doc_path.exists() and not force:
        print(f"Doc exists (skip): {doc_path}")
        return doc_path
    today = dt.date.today().isoformat()
    body = _read_template(root)
    body = body.replace("<Subsystem Name>", title)
    body = body.replace("MY_SUBSYSTEM", slug.upper())
    body = body.replace("YYYY-MM-DD", today)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(body, encoding="utf-8")
    print(f"Wrote {doc_path}")
    return doc_path


def _insert_table_row(content: str, marker: str, row: str) -> str:
    if row.strip() in content:
        return content
    idx = content.find(marker)
    if idx == -1:
        return content + f"\n{row}\n"
    # insert after marker line (header row + separator assumed present)
    line_end = content.find("\n", idx)
    if line_end == -1:
        return content + "\n" + row
    next_line = content.find("\n", line_end + 1)
    if next_line == -1:
        return content + "\n" + row
    return content[: next_line + 1] + row + "\n" + content[next_line + 1 :]


def _update_agents(root: Path, slug: str, title: str, paths: str, never: str | None) -> None:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        print("AGENTS.md missing — run apply.py first", file=sys.stderr)
        return
    doc = _slug_to_doc(slug)
    text = agents.read_text(encoding="utf-8")

    own_row = f"| `{paths}` | [{doc}]({doc}) |"
    text = _insert_table_row(text, "## Ownership map — which doc to update", own_row)

    map_row = f"| [{doc}]({doc}) | 3 | {title} subsystem deep ref |"
    text = _insert_table_row(text, "## Doc map / index", map_row)

    pointer = f"""
### {title} → [{doc}]({doc})

TODO: one paragraph — what it does, where it runs, what to read first.
"""
    if never:
        pointer += f"\n**NEVER:** {never}\n"

    anchor = "## Subsystem pointers"
    if anchor in text and f"### {title} →" not in text:
        text = text.replace(anchor, anchor + pointer)

    agents.write_text(text, encoding="utf-8")
    print(f"Updated {agents}")


def _update_docs_readme(root: Path, slug: str, title: str, paths: str, test: str) -> None:
    readme = root / "docs" / "README.md"
    if not readme.is_file():
        print("docs/README.md missing — run apply.py first", file=sys.stderr)
        return
    doc = _slug_to_doc(slug)
    doc_name = Path(doc).name
    text = readme.read_text(encoding="utf-8")

    router_row = f"| Change {title.lower()} | [{doc_name}]({doc_name}) | [ARCHITECTURE.md](ARCHITECTURE.md) | `{test}` |"
    text = _insert_table_row(text, "## Agent task router", router_row)

    tier_row = f"| [{doc}]({doc_name}) | {title} |"
    text = _insert_table_row(text, "## Tier 3 — Subsystem deep refs", tier_row)

    readme.write_text(text, encoding="utf-8")
    print(f"Updated {readme}")


def _update_state(root: Path, slug: str, title: str, paths: str, test: str) -> None:
    state_path = root / "agent_memory.state.yaml"
    if not state_path.is_file():
        return
    try:
        import yaml
    except ImportError:
        print("PyYAML not installed — skip state update", file=sys.stderr)
        return
    data = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    subs = data.setdefault("subsystems", [])
    entry = {
        "slug": slug,
        "title": title,
        "doc": _slug_to_doc(slug),
        "paths": [p.strip() for p in paths.split(",")],
        "test": test,
    }
    subs = [s for s in subs if s.get("slug") != slug]
    subs.append(entry)
    data["subsystems"] = subs
    state_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")
    print(f"Updated {state_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a new subsystem in agent memory")
    parser.add_argument("--slug", required=True, help="Lowercase identifier, e.g. auth")
    parser.add_argument("--title", required=True, help="Human title, e.g. Authentication")
    parser.add_argument("--paths", required=True, help="Glob(s) for ownership map, comma-separated")
    parser.add_argument("--test", default="pytest -q", help="Representative test command")
    parser.add_argument("--never", help="Optional NEVER invariant line")
    parser.add_argument("--force", action="store_true", help="Overwrite existing deep ref")
    args = parser.parse_args()

    if not SLUG_RE.match(args.slug):
        print("slug must match ^[a-z][a-z0-9_]*$", file=sys.stderr)
        return 1

    root = _repo_root()
    _ensure_doc(root, args.slug, args.title, args.force)
    _update_agents(root, args.slug, args.title, args.paths, args.never)
    _update_docs_readme(root, args.slug, args.title, args.paths, args.test)
    _update_state(root, args.slug, args.title, args.paths, args.test)

    print("\nComplete docs/" + args.slug.upper() + ".md sections per SUBSYSTEM_TEMPLATE.md")
    print("Run: python3 scripts/docs_integrity.py && pytest tests/test_docs_integrity.py -q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
