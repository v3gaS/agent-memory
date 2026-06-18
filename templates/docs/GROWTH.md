---
Last reconciled: {{DATE}}
Scope: Maturity levels L0 → L4 — promote artifacts as the project grows.
---

# GROWTH — Agent memory maturity

Track current level in [agent_memory.state.yaml](../agent_memory.state.yaml).

Full guide (if vendored from scaffold): `scaffold/agent-memory/GROWTH.md`.

---

## Level overview

| Level | When | You have |
| --- | --- | --- |
| **L0** | Idea / spike | README only |
| **L1** | First meaningful code | AGENTS.md, docs/README, one deep ref, .cursorrules |
| **L2** | Agent/team cadence | + BACKLOG, FINDINGS, proposals/, OPERATIONS, docs_integrity + test |
| **L3** | 3+ subsystems | + CONFIG, DATA_MODEL, CLI, MODULE_ONBOARDING, full ownership map |
| **L4** | Long-lived production | + API_CATALOG, help/, __ARCHIVE/ audits, `.cursor/rules/*.mdc`, CI |

**Rule:** promote when pain appears — not preemptively.

---

## Promotion checklist (abbreviated)

### → L2

- Seed [BACKLOG.md](BACKLOG.md)
- Enable [FINDINGS.md](FINDINGS.md)
- CI: `python3 scripts/docs_integrity.py` + `pytest tests/test_docs_integrity.py`

### → L3

- `python3 scripts/register_subsystem.py` per boundary
- Expand [OPERATIONS.md](OPERATIONS.md) (8+ symptoms)
- Complete CONFIG + DATA_MODEL if applicable

### → L4

- Add [API_CATALOG.md](API_CATALOG.md)
- User help copy if product has UI
- Domain `.mdc` rules under `.cursor/rules/`
- Audit snapshots under `__ARCHIVE/`

---

## Self-adjustment

Edit `agent_memory.state.yaml`:

- `maturity_level`
- `subsystems[]` — append when registering new areas
- `integrity.required_docs` — add optional docs as they become mandatory

Extend `scripts/docs_integrity.py` with project-specific semantic guards at L4.

---

## Changelog

- **{{DATE}}** — Growth guide copied from agent-memory scaffold.
