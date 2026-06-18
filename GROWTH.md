# GROWTH — Maturity levels L0 → L4

The scaffold is designed to **start small** and **promote** artifacts as the project
gains subsystems, operators, and agent traffic. Track level in `agent_memory.state.yaml`.

---

## Level overview

| Level | When | You have |
| --- | --- | --- |
| **L0** | Idea / spike | README only |
| **L1** | First meaningful code | AGENTS.md, docs/README, one deep ref, .cursorrules, state yaml |
| **L2** | Team or agent cadence | + BACKLOG, FINDINGS, proposals/, OPERATIONS, docs_integrity + test |
| **L3** | 3+ subsystems, ops burden | + full ownership map, subsystem pointers, CONFIG, DATA_MODEL, CLI, MODULE_ONBOARDING |
| **L4** | Long-lived production | + API_CATALOG, help/ UX copy, agent_db JSON, audit archives, CI guardrails, domain `.mdc` rules |

**Rule:** do not jump to L4 on day one. Promote when pain appears, not preemptively.

---

## Promotion triggers

### L0 → L1

**Trigger:** second contributor, or first agent session that lost context.

**Actions:**

1. Run `apply.py`.
2. Write `docs/CORE.md` (or rename first subsystem).
3. Document stack + run command in ARCHITECTURE + SETUP.

### L1 → L2

**Trigger:** repeated “what should we build?” or doc drift after merges.

**Actions:**

1. Seed BACKLOG with real items (BL-001…).
2. Enable FINDINGS for open bugs.
3. Add `docs/proposals/README.md` discipline to `.cursorrules`.
4. Wire `tests/test_docs_integrity.py` into CI.

### L2 → L3

**Trigger:** third subsystem, or first production incident needing runbook.

**Actions:**

1. `register_subsystem.py` for each boundary.
2. Expand OPERATIONS.md (8+ symptom rows).
3. Add CONFIG.md + DATA_MODEL.md if config/schemas exist.
4. Add CLI.md if commands/scripts exist.
5. Genericize MODULE_ONBOARDING for your module layout.

### L3 → L4

**Trigger:** external APIs, user-facing product, audits, multi-agent throughput.

**Actions:**

1. `docs/API_CATALOG.md` — every external endpoint with curl/examples.
2. `docs/help/` — plain-language UX copy (if product has UI).
3. `.cursor/rules/*.mdc` — per-domain guardrails (API docs fetch, UI language).
4. `__ARCHIVE/audit-YYYY-MM-DD/` — frozen review snapshots.
5. Optional `docs/agent_db/` — JSON registry for symbol/subsystem index.
6. Extend `docs_integrity.py` with project-specific semantic guards.

---

## Self-adjustment via `agent_memory.state.yaml`

Update this file when the project changes shape. Tools and agents should read it.

```yaml
maturity_level: L2
stack: "Next.js 15 + Postgres + tRPC"
primary_config: "apps/web/.env.local"
src_roots:
  - "apps/web/"
  - "packages/core/"
default_test_command: "npm test"
subsystems:
  - slug: core
    doc: docs/CORE.md
    paths: ["packages/core/**"]
    test: "npm test --workspace=@app/core"
integrity:
  required_docs:
    - AGENTS.md
    - docs/README.md
  optional_docs:   # promote to required at L3
    - docs/API_CATALOG.md
```

When you add a subsystem, append to `subsystems` and run `register_subsystem.py`.

When you promote maturity, add optional docs to `integrity.required_docs` and extend
`scripts/docs_integrity.py` checks (see template comments).

---

## Subsystem vs feature

| Create new deep ref when… | Keep in parent doc when… |
| --- | --- |
| Separate deployable or process | Single module, < ~5 public entry points |
| Own config namespace | Helper functions only |
| Distinct on-call/runbook | UI subsection of one app |
| Agent would edit without reading rest | Trivial CRUD extension |

---

## Doc size discipline

| File | Target size | If exceeded |
| --- | --- | --- |
| AGENTS.md | < 400 lines | Move subsystem detail to pointers only |
| Deep ref | < 800 lines | Split sub-doc or add § appendix |
| BACKLOG | Rank + link | Detail in FINDINGS / proposals / archive |
| FINDINGS | Open items only | Archive resolved to `__ARCHIVE/` |

---

## CI recommendation (L2+)

```yaml
# .github/workflows/docs-integrity.yml (example)
- run: python3 scripts/docs_integrity.py
- run: python3 -m pytest tests/test_docs_integrity.py -q
```

Add subsystem test commands to PR template: “Task router Tests column run and output attached.”

---

## Changelog

- **{{DATE}}** — Initial growth guide for agent-memory scaffold.
