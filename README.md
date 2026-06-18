# agent-memory

[![Template](https://img.shields.io/badge/GitHub-template-blue)](https://github.com/v3gaS/agent-memory/generate)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Agent memory** — a portable documentation + Cursor/agent-rules system for any codebase.
Gives humans and coding agents durable context: thin index (`AGENTS.md`), subsystem deep refs,
work portfolio, test discipline, and integrity CI.

Works with **any stack** (Python, Node, Go, Rust, mobile, monorepo). Starts at maturity **L1**;
grow to **L4** as subsystems and ops burden increase ([GROWTH.md](GROWTH.md)).

> Replace `v3gaS` in URLs below when you publish this repository.

---

## Install (fastest)

### curl one-liner (no clone)

```bash
curl -fsSL https://raw.githubusercontent.com/v3gaS/agent-memory/main/install.sh | bash -s -- --target /path/to/your-project
```

Interactive prompts ask for project name, stack, config path, and test command.

### Non-interactive with preset

```bash
curl -fsSL https://raw.githubusercontent.com/v3gaS/agent-memory/main/install.sh | bash -s -- \
  --target . \
  --yes \
  --preset node \
  --project-name "My App"
```

Presets: `python` | `node` | `go` | `rust` (set config path, src root, default test command).

### Clone + local install

```bash
git clone https://github.com/v3gaS/agent-memory.git
./agent-memory/install.sh --local --target /path/to/your-project
```

### PowerShell

```powershell
git clone https://github.com/v3gaS/agent-memory.git
cd agent-memory
.\install.ps1 -Target C:\dev\my-app -Yes -Preset python -ProjectName "My App"
```

### Make

```bash
git clone https://github.com/v3gaS/agent-memory.git
cd agent-memory
make install TARGET=../my-app
```

---

## Verify

After install, in **your project** (not this template repo):

```bash
python3 scripts/docs_integrity.py
python3 -m pytest tests/test_docs_integrity.py -q
# your stack tests:
pytest -q          # or npm test, go test ./..., cargo test
```

**Test discipline:** never weaken assertions to green CI — embedded in `AGENTS.md` and `.cursorrules`.

---

## What gets installed into your project

| File | Role |
| --- | --- |
| `AGENTS.md` | Always-on index — ownership map, NEVER lines |
| `.cursorrules` | Agent ship checklist + conflict order |
| `docs/README.md` | Task router — read X, run test Y |
| `docs/CORE.md` | First subsystem deep ref |
| `docs/BACKLOG.md` / `FINDINGS.md` | Work portfolio + triage |
| `docs/proposals/` | Deferred plan follow-ups |
| `agent_memory.state.yaml` | Machine-readable maturity + subsystems |
| `scripts/docs_integrity.py` | Link + contract checks |
| `tests/test_docs_integrity.py` | Doc system regression tests |

Full layout: [BOOTSTRAP.md](BOOTSTRAP.md).

---

## Grow the system

```bash
# Add a subsystem (from your project root)
python3 scripts/register_subsystem.py \
  --slug auth \
  --title "Authentication" \
  --paths "src/auth/**" \
  --test "pytest tests/test_auth.py -q" \
  --never "Never store passwords in plaintext"
```

Bump `maturity_level` in `agent_memory.state.yaml` when promoting tiers ([GROWTH.md](GROWTH.md)).

CLI wrapper (from cloned template repo):

```bash
./bin/agent-memory install --target ../my-app
./bin/agent-memory verify ../my-app
```

---

## Publish / maintain this template

Maintainers exporting from the Stock Scanner monorepo: [PUBLISH.md](PUBLISH.md).

```bash
./scripts/export-standalone.sh ../agent-memory
cd ../agent-memory && git init && gh repo create v3gaS/agent-memory --public --source=. --push
# GitHub → Settings → Template repository ✓
```

---

## Design principles

1. **Conflict order:** `code + config` → `docs/*` deep refs → `AGENTS.md` (index only)
2. **Same-commit docs:** behavior changes ship doc deltas together
3. **Thin index:** AGENTS.md links; never mirrors deep refs
4. **Tests are intent:** fix code or fix test design — never weaken to pass
5. **Organic growth:** L1 → L4 per [GROWTH.md](GROWTH.md)

---

## Repository layout (this template repo)

```
agent-memory/                 ← standalone template repo root
├── install.sh / install.ps1  ← primary installers
├── apply.py                  ← template copy engine
├── register_subsystem.py
├── bin/agent-memory          ← CLI wrapper
├── templates/                ← files copied into target projects
├── BOOTSTRAP.md / GROWTH.md / PUBLISH.md
├── copier.yml                ← optional Copier flow
└── tests/test_template_repo.py
```

---

## Origin

Extracted from the [Stock Scanner API](https://github.com/) agent/documentation system and generalized for any project.

## License

MIT — see [LICENSE](LICENSE).
