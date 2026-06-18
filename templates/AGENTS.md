# AGENTS.md — {{PROJECT_NAME}} (always-on core)

---
Scope: Orientation, documentation discipline, ownership map, cross-cutting invariants, doc index.
Deep behaviour: [docs/README.md](docs/README.md).
Live triage: [docs/BACKLOG.md](docs/BACKLOG.md), [docs/FINDINGS.md](docs/FINDINGS.md).
Maturity: see [agent_memory.state.yaml](agent_memory.state.yaml) and [GROWTH.md](docs/GROWTH.md) if present.
---

Always-on context for agents working in this repo.

**Conflict rule:** runtime behaviour is defined by **code + `{{PRIMARY_CONFIG}}`**;
subsystem docs in **`docs/*.md`** come next; **this file** is the index only.

> Full deep-reference library: [docs/README.md](docs/README.md). Do not mirror deep refs here.

---

<a id="documentation-contract"></a>

## Documentation discipline — STANDING RULE

When you change a subsystem, update its **deep ref** in `docs/` in the **same commit**:
API/schema rows, invariants list, and that doc's **own changelog**. Not a follow-up, not a TODO.

Update **AGENTS.md** only when:

1. You **added or removed a subsystem** → doc map + pointer below.
2. You changed a **cross-cutting invariant** (owned by no single doc).
3. You changed a **never-violate safety invariant** → update that pointer's **NEVER** line.

Otherwise **AGENTS.md does not change**. History lives in each deep ref's changelog.

**Forbidden:**

- Mirroring a deep ref's full content into a pointer ("AGENTS should be enough").
- Adding a changelog section to AGENTS.md.
- "Will doc in a follow-up." Doc drift is the failure mode this system prevents.

**New subsystem:** copy [docs/SUBSYSTEM_TEMPLATE.md](docs/SUBSYSTEM_TEMPLATE.md) → `docs/<NAME>.md`,
or run `python3 scripts/register_subsystem.py`, then add ownership + doc-map + pointer rows here in the same commit.

---

## Test discipline — STANDING RULE

When you touch a subsystem:

1. Run the **Tests** command from [docs/README.md](docs/README.md) agent task router for that area.
2. Run `python3 scripts/docs_integrity.py` after markdown edits.
3. Run `python3 -m pytest tests/test_docs_integrity.py -q` (doc system regression).

**When tests fail, never weaken the test to gain a pass.** Do not delete assertions, widen
tolerances without documented approval, or skip/xfail to green without a tracked `F-###` item.
Fix the code, or fix the test if the *intent* was wrong — and document why in the deep ref or FINDINGS.

Default project test command: `{{DEFAULT_TEST_COMMAND}}`

---

## Ownership map — which doc to update

| If you edit… | Update doc(s) |
| --- | --- |
| `{{SRC_ROOT}}**` (core application) | [docs/CORE.md](docs/CORE.md) |
| `{{PRIMARY_CONFIG}}`, env example | [docs/CONFIG.md](docs/CONFIG.md) |
| Schemas, migrations, persisted shapes | [docs/DATA_MODEL.md](docs/DATA_MODEL.md) |
| CLI, scripts, Makefile targets | [docs/CLI.md](docs/CLI.md) |
| Cross-cutting ops symptoms | [docs/OPERATIONS.md](docs/OPERATIONS.md) |
| Work portfolio / roadmap | [docs/BACKLOG.md](docs/BACKLOG.md) |

<!-- register_subsystem.py appends rows below -->

---

## Cross-cutting invariants

### Stack

**Shipped stack:** {{STACK_SUMMARY}}

Do not substitute frameworks or runtimes without an explicit project decision recorded in BACKLOG.

### Primary config

**Authority:** `{{PRIMARY_CONFIG}}` + code. Document new keys in [docs/CONFIG.md](docs/CONFIG.md).

---

## Operations triage — symptom → doc

| Symptom | See |
| --- | --- |
| App won't start / build fails | [docs/OPERATIONS.md §1](docs/OPERATIONS.md#1-app-wont-start--build-fails) |
| Tests failing | [docs/OPERATIONS.md §2](docs/OPERATIONS.md#2-tests-failing) |
| Doc vs code mismatch | [docs/FINDINGS.md](docs/FINDINGS.md) + `python3 scripts/docs_integrity.py` |
| What to build next | [docs/BACKLOG.md](docs/BACKLOG.md) |

---

## Doc map / index

| Doc | Tier | Purpose |
| --- | --- | --- |
| [README.md](README.md) | 1 | Overview, quick start |
| [docs/README.md](docs/README.md) | 1 | Navigator + task router |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 1 | Topology, modules |
| [docs/SETUP.md](docs/SETUP.md) | 1 | Install and local dev |
| [docs/CLI.md](docs/CLI.md) | 1 | Commands and flags |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | 2 | Symptom runbook |
| [docs/CONFIG.md](docs/CONFIG.md) | 2 | Settings reference |
| [docs/BACKLOG.md](docs/BACKLOG.md) | 2 | Work portfolio |
| [docs/FINDINGS.md](docs/FINDINGS.md) | 2 | Live `F-###` triage |
| [docs/CORE.md](docs/CORE.md) | 3 | Core subsystem deep ref |
| [docs/SUBSYSTEM_TEMPLATE.md](docs/SUBSYSTEM_TEMPLATE.md) | 5 | New subsystem skeleton |
| [docs/MODULE_ONBOARDING.md](docs/MODULE_ONBOARDING.md) | 5 | Module integration gate |
| [docs/proposals/README.md](docs/proposals/README.md) | 5 | Deferred plan follow-ups |

---

## Subsystem pointers

### Core → [docs/CORE.md](docs/CORE.md)

Primary application logic under `{{SRC_ROOT}}`. Read before editing core domain code.

**NEVER:** ship behavior changes without the matching deep-ref changelog in the same commit.

<!-- register_subsystem.py appends pointers below -->
