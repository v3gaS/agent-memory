#!/usr/bin/env python3
"""Detect project stack from repo markers and sync agent_memory profile.

Usage:
  python3 stack_detect.py --root /path/to/project
  python3 stack_detect.py --root . --sync
  python3 stack_detect.py --root . --sync --replace

Copied to target projects as scripts/stack_detect.py by apply.py.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


MARKERS: list[tuple[str, str, str]] = [
    ("pyproject.toml", "python", "Python (pyproject.toml)"),
    ("requirements.txt", "python", "Python (requirements.txt)"),
    ("requirements-dev.txt", "python", "Python (requirements-dev.txt)"),
    ("setup.py", "python", "Python (setup.py)"),
    ("Pipfile", "python", "Python (Pipfile)"),
    ("package.json", "node", "Node.js (package.json)"),
    ("pnpm-workspace.yaml", "pnpm-monorepo", "pnpm monorepo"),
    ("turbo.json", "turborepo", "Turborepo"),
    ("nx.json", "nx", "Nx monorepo"),
    ("lerna.json", "lerna", "Lerna monorepo"),
    ("go.mod", "go", "Go"),
    ("Cargo.toml", "rust", "Rust (Cargo)"),
    ("Gemfile", "ruby", "Ruby (Bundler)"),
    ("composer.json", "php", "PHP (Composer)"),
    ("mix.exs", "elixir", "Elixir (Mix)"),
    ("deno.json", "deno", "Deno"),
    ("deno.jsonc", "deno", "Deno"),
    ("pubspec.yaml", "flutter", "Flutter/Dart"),
    ("pom.xml", "java-maven", "Java (Maven)"),
    ("build.gradle", "java-gradle", "Java/Kotlin (Gradle)"),
    ("build.gradle.kts", "java-gradle", "Java/Kotlin (Gradle Kotlin DSL)"),
    ("Dockerfile", "docker", "Docker"),
    ("docker-compose.yml", "docker-compose", "Docker Compose"),
    ("docker-compose.yaml", "docker-compose", "Docker Compose"),
    (".env.example", "dotenv", "Environment config (.env)"),
    ("config/settings.yaml", "yaml-config", "YAML config (config/settings.yaml)"),
]

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build",
    ".turbo", ".next", "target", "vendor", "scaffold",
}

DEFAULT_STACK_PLACEHOLDER = "Describe your stack here (language, framework, datastore, deploy target)"


@dataclass
class StackSignal:
    id: str
    label: str
    evidence: str
    first_seen: str = ""
    last_seen: str = ""


@dataclass
class StackProfile:
    summary: str
    signals: list[StackSignal] = field(default_factory=list)
    primary_config: str = ""
    src_roots: list[str] = field(default_factory=list)
    default_test_command: str = ""
    detected_at: str = ""


def _today() -> str:
    return dt.date.today().isoformat()


def _read_text(path: Path, limit: int = 64_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _walk_markers(root: Path, max_depth: int = 4) -> list[StackSignal]:
    found: dict[str, StackSignal] = {}
    today = _today()

    def consider(rel: str, sid: str, label: str) -> None:
        key = f"{sid}:{rel}"
        if key in found:
            return
        found[key] = StackSignal(id=sid, label=label, evidence=rel, first_seen=today, last_seen=today)

    for name, sid, label in MARKERS:
        if (root / name).is_file():
            consider(name, sid, label)

    for pattern in ("apps/*/package.json", "packages/*/package.json", "apps/*/pyproject.toml"):
        for p in root.glob(pattern):
            if p.is_file():
                rel = p.relative_to(root).as_posix()
                if rel.endswith("package.json"):
                    consider(rel, "node", f"Node.js ({rel})")
                else:
                    consider(rel, "python", f"Python ({rel})")

    def walk(dir_path: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = list(dir_path.iterdir())
        except OSError:
            return
        for entry in entries:
            if entry.name in SKIP_DIRS or not entry.is_dir():
                continue
            for name, sid, label in MARKERS:
                candidate = entry / name
                if candidate.is_file():
                    rel = candidate.relative_to(root).as_posix()
                    short = label.split("(")[0].strip()
                    consider(rel, sid, f"{short} ({rel})")
            walk(entry, depth + 1)

    for top in ("apps", "packages", "services", "cmd", "internal", "src"):
        d = root / top
        if d.is_dir():
            walk(d, 1)

    return list(found.values())


def _enrich_from_package_json(root: Path) -> list[str]:
    hints: list[str] = []
    pkg_files = [root / "package.json", *root.glob("apps/*/package.json"), *root.glob("packages/*/package.json")]
    framework_map = {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue",
        "@angular/core": "Angular",
        "svelte": "Svelte",
        "express": "Express",
        "fastify": "Fastify",
        "@nestjs/core": "NestJS",
        "@remix-run/react": "Remix",
        "nuxt": "Nuxt",
        "electron": "Electron",
    }
    for pkg_path in pkg_files:
        if not pkg_path.is_file():
            continue
        try:
            data = json.loads(_read_text(pkg_path))
        except json.JSONDecodeError:
            continue
        deps: dict[str, Any] = {}
        for k in ("dependencies", "devDependencies", "peerDependencies"):
            if isinstance(data.get(k), dict):
                deps.update(data[k])
        for dep, fw in framework_map.items():
            if dep in deps and fw not in hints:
                hints.append(fw)
    return hints


def _enrich_from_pyproject(root: Path) -> list[str]:
    hints: list[str] = []
    for path in [root / "pyproject.toml", *root.glob("apps/*/pyproject.toml")]:
        if not path.is_file():
            continue
        text = _read_text(path).lower()
        for fw, label in (
            ("fastapi", "FastAPI"),
            ("django", "Django"),
            ("flask", "Flask"),
            ("dash", "Dash"),
            ("pytest", "pytest"),
            ("uvicorn", "ASGI/uvicorn"),
        ):
            if fw in text and label not in hints:
                hints.append(label)
    return hints


def _guess_primary_config(root: Path, signals: list[StackSignal]) -> str:
    for c in (
        "config/settings.yaml", "config.yaml", "config.yml", ".env", ".env.local",
        "application.yml", "application.yaml", "appsettings.json",
    ):
        if (root / c).is_file():
            return c
    for s in signals:
        if s.id == "dotenv":
            return ".env.example" if (root / ".env.example").is_file() else ".env"
        if s.id == "yaml-config":
            return s.evidence
    return "config/settings.yaml"


def _guess_src_roots(root: Path, signals: list[StackSignal]) -> list[str]:
    roots: list[str] = []
    for name in ("src", "lib", "app", "apps", "packages", "internal", "cmd"):
        if (root / name).exists() and f"{name}/" not in roots:
            roots.append(f"{name}/")
    if roots:
        return roots[:5]
    if any(s.id == "go" for s in signals):
        return ["./"]
    return ["src/"]


def _guess_test_command(root: Path, signals: list[StackSignal]) -> str:
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            scripts = (json.loads(_read_text(pkg)) or {}).get("scripts") or {}
            if isinstance(scripts, dict) and scripts.get("test"):
                pm = "pnpm" if (root / "pnpm-lock.yaml").is_file() else "npm"
                return f"{pm} test"
        except json.JSONDecodeError:
            pass
    if (root / "Cargo.toml").is_file():
        return "cargo test"
    if (root / "go.mod").is_file():
        return "go test ./..."
    if any(s.id == "python" for s in signals) or (root / "pyproject.toml").is_file():
        return "pytest -q"
    if (root / "Makefile").is_file() and "test:" in _read_text(root / "Makefile"):
        return "make test"
    return "pytest -q"


def _build_summary(signals: list[StackSignal], framework_hints: list[str]) -> str:
    id_to_label = {
        "python": "Python",
        "node": "Node.js",
        "go": "Go",
        "rust": "Rust",
        "ruby": "Ruby",
        "php": "PHP",
        "elixir": "Elixir",
        "deno": "Deno",
        "flutter": "Flutter/Dart",
        "java-maven": "Java",
        "java-gradle": "Java/Kotlin",
    }
    bases: list[str] = []
    for s in signals:
        base = id_to_label.get(s.id)
        if base and base not in bases:
            bases.append(base)
    if any(s.id in {"pnpm-monorepo", "turborepo", "nx", "lerna"} for s in signals):
        if "monorepo" not in " ".join(bases).lower():
            bases.append("monorepo")
    for h in framework_hints:
        if h not in bases:
            bases.append(h)
    if not bases:
        return "Application (stack not detected — run stack_detect.py --sync or edit agent_memory.state.yaml)"
    return " + ".join(bases[:8])


def detect_stack(root: Path) -> StackProfile:
    root = root.resolve()
    signals = _walk_markers(root)
    fw_hints = _enrich_from_package_json(root) + _enrich_from_pyproject(root)
    return StackProfile(
        summary=_build_summary(signals, fw_hints),
        signals=signals,
        primary_config=_guess_primary_config(root, signals),
        src_roots=_guess_src_roots(root, signals),
        default_test_command=_guess_test_command(root, signals),
        detected_at=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    )


def _merge_signals(existing: list[dict], detected: list[StackSignal]) -> list[dict]:
    by_key: dict[str, dict] = {}
    today = _today()
    for item in existing:
        if isinstance(item, dict) and item.get("id") and item.get("evidence"):
            by_key[f"{item['id']}:{item['evidence']}"] = item
    for sig in detected:
        key = f"{sig.id}:{sig.evidence}"
        if key in by_key:
            by_key[key]["last_seen"] = today
            by_key[key]["label"] = sig.label
        else:
            by_key[key] = asdict(sig)
    return sorted(by_key.values(), key=lambda x: (x.get("id", ""), x.get("evidence", "")))


def _rebuild_summary_from_state(state: dict) -> str:
    signals = [
        StackSignal(id=s.get("id", ""), label=s.get("label", ""), evidence=s.get("evidence", ""))
        for s in (state.get("stack_signals") or [])
        if isinstance(s, dict)
    ]
    manual = state.get("stack_manual_append") or []
    hints = list(manual) if isinstance(manual, list) else []
    return _build_summary(signals, hints)


def _patch_line(content: str, pattern: str, replacement: str) -> str:
    if re.search(pattern, content, flags=re.MULTILINE):
        return re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE)
    return content


def sync_profile(root: Path, *, replace: bool = False, dry_run: bool = False) -> StackProfile:
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")

    root = root.resolve()
    detected = detect_stack(root)
    state_path = root / "agent_memory.state.yaml"
    state: dict = {}
    if state_path.is_file() and not replace:
        state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}

    merged_signals = _merge_signals([] if replace else (state.get("stack_signals") or []), detected.signals)
    state["stack_signals"] = merged_signals
    state["stack"] = _rebuild_summary_from_state({**state, "stack_signals": merged_signals})
    state["stack_last_sync"] = _today()
    profile_block = state.setdefault("stack_profile", {})
    if isinstance(profile_block, dict):
        profile_block["auto_detect"] = True
        profile_block["last_detected_at"] = detected.detected_at

    if not state.get("primary_config") or state.get("primary_config") == "config/settings.yaml":
        if detected.primary_config != "config/settings.yaml" or not (root / "config/settings.yaml").is_file():
            state["primary_config"] = detected.primary_config
    if not state.get("src_roots"):
        state["src_roots"] = detected.src_roots
    if not state.get("default_test_command") or state.get("default_test_command") == "pytest -q":
        state["default_test_command"] = detected.default_test_command

    if not dry_run:
        state_path.write_text(yaml.dump(state, default_flow_style=False, sort_keys=False), encoding="utf-8")
        print(f"updated {state_path.relative_to(root)}")

        proj = root / "agent_memory.project.yaml"
        if proj.is_file():
            proj_data = yaml.safe_load(proj.read_text(encoding="utf-8")) or {}
            proj_data["stack_summary"] = state["stack"]
            proj.write_text(yaml.dump(proj_data, default_flow_style=False, sort_keys=False), encoding="utf-8")
            print(f"updated {proj.relative_to(root)}")

        stack_line = state["stack"]
        for doc_path, pattern in (
            (root / "AGENTS.md", r"^\*\*Shipped stack:\*\*.*$"),
            (root / "docs" / "ARCHITECTURE.md", r"^\*\*Stack:\*\*.*$"),
        ):
            if not doc_path.is_file():
                continue
            text = doc_path.read_text(encoding="utf-8")
            prefix = "**Shipped stack:**" if "AGENTS" in doc_path.name else "**Stack:**"
            new_text = _patch_line(text, pattern, f"{prefix} {stack_line}")
            if new_text != text:
                doc_path.write_text(new_text, encoding="utf-8")
                print(f"updated {doc_path.relative_to(root)}")

    detected.summary = state["stack"]
    return detected


def apply_detection_to_config(cfg: dict, root: Path) -> dict:
    """Fill config from detection when stack was not explicitly provided."""
    explicit = cfg.get("stack_summary", "")
    if explicit and explicit != DEFAULT_STACK_PLACEHOLDER:
        return cfg
    profile = detect_stack(root)
    cfg["stack_summary"] = profile.summary
    if not cfg.get("primary_config") or cfg.get("primary_config") == "config/settings.yaml":
        cfg["primary_config"] = profile.primary_config
    if not cfg.get("src_root") or cfg.get("src_root") == "src/":
        cfg["src_root"] = profile.src_roots[0] if profile.src_roots else "src/"
    if not cfg.get("default_test_command") or cfg.get("default_test_command") == "pytest -q":
        cfg["default_test_command"] = profile.default_test_command
    cfg["_detected_stack_signals"] = [asdict(s) for s in profile.signals]
    return cfg


def write_initial_signals(target: Path, cfg: dict) -> None:
    """After bootstrap, seed stack_signals in agent_memory.state.yaml."""
    if yaml is None:
        return
    state_path = target / "agent_memory.state.yaml"
    if not state_path.is_file():
        return
    state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    signals = cfg.get("_detected_stack_signals") or []
    if signals:
        state["stack_signals"] = signals
        state["stack_last_sync"] = _today()
        state.setdefault("stack_profile", {})["auto_detect"] = True
        state_path.write_text(yaml.dump(state, default_flow_style=False, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect and sync project stack profile")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--sync", action="store_true")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    if args.sync:
        profile = sync_profile(root, replace=args.replace, dry_run=args.dry_run)
    else:
        profile = detect_stack(root)

    payload = {
        "summary": profile.summary,
        "primary_config": profile.primary_config,
        "src_roots": profile.src_roots,
        "default_test_command": profile.default_test_command,
        "signals": [asdict(s) for s in profile.signals],
        "detected_at": profile.detected_at,
    }
    if args.json or not args.sync:
        print(json.dumps(payload, indent=2))
    elif not args.dry_run:
        print(f"stack: {profile.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
