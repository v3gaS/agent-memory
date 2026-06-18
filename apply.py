#!/usr/bin/env python3
"""Bootstrap agent-memory scaffold into a target project.

Usage:
  python3 apply.py --target /path/to/project
  python3 apply.py --target . --config agent_memory.project.yaml
  python3 apply.py --target . --force
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from stack_detect import apply_detection_to_config, detect_stack, write_initial_signals


SCAFFOLD_ROOT = Path(__file__).resolve().parent
TEMPLATES = SCAFFOLD_ROOT / "templates"
DEFAULTS_PATH = SCAFFOLD_ROOT / "config" / "scaffold.defaults.yaml"

PLACEHOLDERS = (
    "{{PROJECT_NAME}}",
    "{{STACK_SUMMARY}}",
    "{{PRIMARY_CONFIG}}",
    "{{SRC_ROOT}}",
    "{{DEFAULT_TEST_COMMAND}}",
    "{{DATE}}",
    "{{MATURITY_LEVEL}}",
)


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _merge_config(config_path: Path | None, args: argparse.Namespace) -> dict:
    cfg: dict = {}
    if DEFAULTS_PATH.is_file():
        cfg.update(_load_yaml(DEFAULTS_PATH))
    if config_path and config_path.is_file():
        cfg.update(_load_yaml(config_path))
    if args.project_name:
        cfg["project_name"] = args.project_name
    if args.stack:
        cfg["stack_summary"] = args.stack
    if args.primary_config:
        cfg["primary_config"] = args.primary_config
    if args.src_root:
        cfg["src_root"] = args.src_root
    if args.test_command:
        cfg["default_test_command"] = args.test_command
    if getattr(args, "no_detect_stack", False):
        cfg["_no_detect_stack"] = True
    if not cfg.get("date"):
        cfg["date"] = dt.date.today().isoformat()
    cfg["force"] = args.force or cfg.get("force", False)
    cfg["skip_existing"] = not args.force and cfg.get("skip_existing", True)
    return cfg


def _prompt(cfg: dict) -> dict:
    def ask(key: str, prompt: str, default: str) -> None:
        if cfg.get(key) and cfg[key] != _load_yaml(DEFAULTS_PATH).get(key):
            return
        val = input(f"{prompt} [{default}]: ").strip()
        cfg[key] = val or default

    defaults = _load_yaml(DEFAULTS_PATH) if DEFAULTS_PATH.is_file() else {}
    detected_default = ""
    if cfg.get("_detect_preview"):
        detected_default = cfg["_detect_preview"]
    ask("project_name", "Project name", cfg.get("project_name") or defaults.get("project_name", "My Project"))
    ask(
        "stack_summary",
        "Stack summary (one line, Enter=detected)",
        cfg.get("stack_summary") or detected_default or defaults.get("stack_summary", ""),
    )
    ask("primary_config", "Primary config path", cfg.get("primary_config") or defaults.get("primary_config", "config/settings.yaml"))
    ask("src_root", "Source root", cfg.get("src_root") or defaults.get("src_root", "src/"))
    ask("test_command", "Default test command", cfg.get("default_test_command") or defaults.get("default_test_command", "pytest -q"))
    cfg.setdefault("maturity_level", "L1")
    cfg.setdefault("date", dt.date.today().isoformat())
    return cfg


def _substitute(text: str, cfg: dict) -> str:
    mapping = {
        "{{PROJECT_NAME}}": str(cfg["project_name"]),
        "{{STACK_SUMMARY}}": str(cfg.get("stack_summary", "")),
        "{{PRIMARY_CONFIG}}": str(cfg.get("primary_config", "config/settings.yaml")),
        "{{SRC_ROOT}}": str(cfg.get("src_root", "src/")),
        "{{DEFAULT_TEST_COMMAND}}": str(cfg.get("default_test_command", "pytest -q")),
        "{{DATE}}": str(cfg.get("date", dt.date.today().isoformat())),
        "{{MATURITY_LEVEL}}": str(cfg.get("maturity_level", "L1")),
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text


def _iter_template_files() -> list[Path]:
    return sorted(p for p in TEMPLATES.rglob("*") if p.is_file())


def _dest_for(rel: Path) -> str:
    name = rel.name
    if name == "README.snippet.md":
        return rel.as_posix()
    if name.endswith(".example"):
        return rel.with_name(name.removesuffix(".example")).as_posix()
    return rel.as_posix()


def apply(target: Path, cfg: dict) -> list[str]:
    actions: list[str] = []
    force = bool(cfg.get("force"))
    skip_existing = bool(cfg.get("skip_existing", True)) and not force

    for src in _iter_template_files():
        rel = src.relative_to(TEMPLATES)
        dest_rel = _dest_for(rel)
        if dest_rel.endswith("README.snippet.md"):
            dest = target / dest_rel
        else:
            dest = target / dest_rel

        if skip_existing and dest.exists():
            actions.append(f"SKIP (exists): {dest_rel}")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = src.read_text(encoding="utf-8")
        dest.write_text(_substitute(raw, cfg), encoding="utf-8")
        actions.append(f"WRITE: {dest_rel}")

    # Copy helper scripts to scripts/ if not from templates
    for helper in ("register_subsystem.py", "stack_detect.py"):
        src = SCAFFOLD_ROOT / helper
        if not src.is_file():
            continue
        dest = target / "scripts" / helper
        if skip_existing and dest.exists():
            actions.append(f"SKIP (exists): scripts/{helper}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        dest.chmod(dest.stat().st_mode | 0o111)
        actions.append(f"WRITE: scripts/{helper}")

    # Write project config for re-runs
    if yaml is not None:
        proj_yaml = target / "agent_memory.project.yaml"
        out = {k: cfg[k] for k in (
            "project_name", "stack_summary", "primary_config", "src_root",
            "default_test_command", "maturity_level", "date",
        ) if k in cfg}
        if not skip_existing or not proj_yaml.exists():
            proj_yaml.write_text(yaml.dump(out, default_flow_style=False, sort_keys=False), encoding="utf-8")
            actions.append("WRITE: agent_memory.project.yaml")

    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply agent-memory scaffold to a project")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="Target project root")
    parser.add_argument("--config", type=Path, help="agent_memory.project.yaml")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    parser.add_argument("--no-prompt", action="store_true", help="Skip interactive prompts")
    parser.add_argument("--project-name", dest="project_name")
    parser.add_argument("--stack")
    parser.add_argument("--primary-config", dest="primary_config")
    parser.add_argument("--src-root", dest="src_root")
    parser.add_argument("--test-command", dest="test_command")
    parser.add_argument(
        "--detect-stack",
        action="store_true",
        default=None,
        help="Auto-detect stack from repo markers (default when --no-prompt and no --stack)",
    )
    parser.add_argument("--no-detect-stack", dest="no_detect_stack", action="store_true")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.is_dir():
        print(f"Target not a directory: {target}", file=sys.stderr)
        return 1

    cfg = _merge_config(args.config, args)

    use_detect = not cfg.get("_no_detect_stack") and not args.stack
    if args.no_detect_stack:
        use_detect = False
    if args.detect_stack:
        use_detect = True

    if use_detect:
        preview = detect_stack(target)
        cfg["_detect_preview"] = preview.summary
        if not args.stack:
            cfg = apply_detection_to_config(cfg, target)
            if args.no_prompt or args.config:
                print(f"Detected stack: {cfg.get('stack_summary')}")

    if not args.no_prompt and not args.config:
        cfg = _prompt(cfg)

    actions = apply(target, cfg)
    if use_detect and cfg.get("_detected_stack_signals"):
        write_initial_signals(target, cfg)
        actions.append("UPDATE: agent_memory.state.yaml stack_signals")
    print(f"\nApplied agent-memory scaffold to {target}\n")
    for line in actions:
        print(f"  {line}")

    print("\nNext steps:")
    print("  1. Complete docs/ARCHITECTURE.md and docs/CORE.md")
    print("  2. Merge templates/README.snippet.md into project README if brownfield")
    print("  3. python3 scripts/docs_integrity.py")
    print(f"  4. python3 -m pytest tests/test_docs_integrity.py -q")
    print(f"  5. {cfg.get('default_test_command', 'pytest -q')}")
    print("  6. After adding new stack pieces: python3 scripts/stack_detect.py --sync")
    print("\nSee BOOTSTRAP.md for full checklist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
