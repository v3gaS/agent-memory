---
Last reconciled: {{DATE}}
Scope: Module integration gate checklist — adapt paths to your stack.
---

# MODULE_ONBOARDING.md — Module Integration Gate

Use when introducing a new module boundary or extracting a subsystem from a monolith.

**Adapt §2** to your layout (`src/`, `packages/`, `apps/`, `internal/`, etc.).

---

## 1. Purpose

Repeatable, low-risk gate for adding modules while preserving runtime behavior and boundaries.

---

## 2. Required module shape (example)

For each new module under `{{SRC_ROOT}}<name>/`:

- Public entry / facade (protocol or exported API)
- `README` or deep ref section §5 API surface
- Tests colocated or under `tests/`

Optional layered internals when complexity grows:

- `domain/` — pure logic
- `application/` — use cases
- `infra/` — IO, DB, HTTP clients
- `adapters/` — external integrations

---

## 3. Non-negotiable boundary rules

1. Cross-module calls go through documented public APIs only.
2. No importing private symbols (`_foo`, `internal/` bypass) across boundaries.
3. Shared kernel / common package holds primitives only — not feature logic.
4. If renaming/moving modules, keep compatibility shims for one stable cycle unless waived.

---

## 4. Onboarding checklist (merge gate)

### 4.1 Contracts first

- [ ] Define public API before moving internals.
- [ ] At least one production call site uses the new boundary.

### 4.2 Compatibility

- [ ] Old import paths still work (shim) or migration guide published.
- [ ] Regression test for old + new paths if shim used.

### 4.3 Tests and validation

- [ ] Module/unit tests added or extended.
- [ ] Run subsystem **Tests** command from [docs/README.md](README.md).
- [ ] Run doc integrity:

```bash
python3 scripts/docs_integrity.py
python3 -m pytest tests/test_docs_integrity.py -q
```

- [ ] Run project suite: `{{DEFAULT_TEST_COMMAND}}`

**Test rule:** never weaken existing tests to pass onboarding — fix code or update documented intent.

### 4.4 Documentation (same change)

- [ ] Subsystem deep ref in `docs/` (from [SUBSYSTEM_TEMPLATE.md](SUBSYSTEM_TEMPLATE.md)).
- [ ] [AGENTS.md](../AGENTS.md) ownership map + pointer (+ doc map if new subsystem).
- [ ] [docs/README.md](README.md) task router row with **Tests** command.
- [ ] Update [agent_memory.state.yaml](../agent_memory.state.yaml) `subsystems` list.

### 4.5 PR requirements

- [ ] Rollback notes in PR description.
- [ ] Prefer one boundary per PR.
- [ ] Extraction PRs: move + adapt only — no drive-by behavior changes.

---

## 5. Shim removal criteria

Remove compatibility shims only when:

- Stable cycle completed without regressions.
- No remaining imports of shim path (grep / CI guard).
- Tests green including doc integrity.
- Rollback path documented.

---

## 6. Changelog

- **{{DATE}}** — Initial generic module onboarding gate (agent-memory scaffold).
