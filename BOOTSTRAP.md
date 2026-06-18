# BOOTSTRAP — Apply Agent Memory to a Project

Use this guide when adding the scaffold to a **new repo** or **existing codebase**.

---

## Prerequisites

- Python 3.10+ (for `apply.py`, `docs_integrity.py`, `register_subsystem.py`)
- Git repo (recommended)
- Cursor or another agent that reads `.cursorrules` and `AGENTS.md`

---

## Mode A — install.sh (recommended)

From the **target project root** (or any path):

```bash
# Remote (after publishing standalone repo — replace v3gaS)
curl -fsSL https://raw.githubusercontent.com/v3gaS/agent-memory/main/install.sh | bash -s -- --target .

# Local (from cloned template repo)
/path/to/agent-memory/install.sh --local --target .

# Non-interactive preset
./install.sh --local --target . --yes --preset python --project-name "My App"
```

`install.sh` runs `apply.py`, installs PyYAML/pytest if needed, and verifies docs integrity by default.

---

## Mode B — apply.py directly

From the **target project root**:

```bash
python3 /path/to/agent-memory/apply.py --target .
python3 /path/to/agent-memory/apply.py --target . --config agent_memory.project.yaml --no-prompt
```

The script will:

1. Ask for project name, stack summary, primary config path, source root, default test command (unless `--no-prompt` / `--config`).
2. Copy `templates/**` into the target (skips files that already exist unless `--force`).
3. Write `agent_memory.state.yaml` at project root.
4. Write `agent_memory.project.yaml` (your answers — safe to commit).
5. Print a post-apply checklist.

---

## Mode C — Manual copy

If you cannot run Python on the target machine:

1. Copy everything under `templates/` into the project root (preserve paths).
2. Replace placeholders manually (search for `{{` in copied files):
   - `{{PROJECT_NAME}}`
   - `{{STACK_SUMMARY}}`
   - `{{PRIMARY_CONFIG}}`
   - `{{SRC_ROOT}}`
   - `{{DEFAULT_TEST_COMMAND}}`
   - `{{DATE}}` (YYYY-MM-DD)
3. Copy `apply.py` helpers into `scripts/` if desired (`register_subsystem.py`).

---

## Post-apply checklist (required)

- [ ] Fill [docs/ARCHITECTURE.md](templates/docs/ARCHITECTURE.md) with real topology.
- [ ] Fill [docs/SETUP.md](templates/docs/SETUP.md) with install steps.
- [ ] Rename or replace `docs/CORE.md` — first subsystem deep ref.
- [ ] Add 3+ rows to [docs/BACKLOG.md](templates/docs/BACKLOG.md).
- [ ] Merge doc pointer into project [README.md](templates/README.snippet.md) (do not replace entire README on brownfield).
- [ ] Run integrity + tests:

```bash
python3 scripts/docs_integrity.py
python3 -m pytest tests/test_docs_integrity.py -q
{{DEFAULT_TEST_COMMAND}}
```

- [ ] Commit scaffold + config in one commit: `chore: bootstrap agent memory doc system`

---

## Adding a subsystem later

When a new bounded area appears (auth, billing, worker, UI shell, etc.):

```bash
python3 scripts/register_subsystem.py \
  --slug billing \
  --title "Billing" \
  --paths "src/billing/**,packages/billing/**" \
  --test "pytest tests/test_billing.py -q" \
  --never "Never charge a card without idempotency key"
```

Then open `docs/BILLING.md` and complete [SUBSYSTEM_TEMPLATE.md](templates/docs/SUBSYSTEM_TEMPLATE.md) sections.

Update `agent_memory.state.yaml`:

```yaml
maturity_level: L2   # bump when appropriate — see GROWTH.md
subsystems:
  - slug: billing
    doc: docs/BILLING.md
    paths: ["src/billing/**"]
```

---

## Brownfield (existing repo) notes

| Situation | Action |
| --- | --- |
| README already exists | Apply with default `--skip-existing`; merge `README.snippet.md` section only |
| `docs/` folder exists | Apply with `--skip-existing`; merge task router rows by hand |
| Different test runner | Set `default_test_command` in project yaml (`npm test`, `go test ./...`, `cargo test`) |
| Monorepo | Set `src_root` to `apps/api/` or list multiple paths in ownership map |
| Non-Python project | Keep `scripts/*.py` for doc tooling; tests run via pytest only for doc integrity |

---

## Test discipline (non-negotiable)

Agents and humans **must**:

1. Run the **Tests** column command from [docs/README.md](templates/docs/README.md) task router when touching a subsystem.
2. Run `python3 scripts/docs_integrity.py` after markdown edits.
3. Run `pytest tests/test_docs_integrity.py` in CI or pre-push.

**Never** alter tests to pass without fixing the underlying behavior:

- Do not delete assertions.
- Do not widen tolerances without documented reason in FINDINGS or deep ref.
- Do not skip/xfail to green unless tracked as `F-###` with owner approval.

This rule is embedded in `.cursorrules` and [AGENTS.md](templates/AGENTS.md).

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `apply.py` skips files | Use `--force` for specific path or delete stale stub |
| Broken links in integrity | Fix relative paths; external URLs are not checked |
| AGENTS.md grows too large | Move detail to deep refs; keep only pointers + NEVER |
| Too many subsystems | Tier 3 only for major boundaries; small features stay in parent deep ref |

See [GROWTH.md](GROWTH.md) for when to add API catalogs, help/, proposals per subsystem, and CI workflows.
