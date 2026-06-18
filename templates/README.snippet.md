## Documentation & agent memory

This project uses an **agent memory** documentation system for humans and coding agents.

| Start here | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Always-on index — ownership map, invariants, test rules |
| [docs/README.md](docs/README.md) | Task router — which doc to read, which tests to run |
| [docs/BACKLOG.md](docs/BACKLOG.md) | What to build or fix next |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Symptom-first runbook |

**Conflict order:** code + config → subsystem deep refs in `docs/` → `AGENTS.md` (index only).

**Tests:** never weaken assertions to green CI — fix code or fix test intent; see AGENTS.md test discipline.

Bootstrap / growth guide: if this repo was scaffolded from `scaffold/agent-memory/`, see that folder's `BOOTSTRAP.md` and `GROWTH.md`.
