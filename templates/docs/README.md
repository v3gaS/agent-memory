---
Last reconciled: {{DATE}}
Scope: Five-tier documentation index and agent task router.
---

# docs/ — {{PROJECT_NAME}} Documentation

Start here. Docs are organised into **five tiers**, each answering a different question.

> **Root entry points:** [README.md](../README.md), [AGENTS.md](../AGENTS.md) (slim index + documentation discipline).

**Conflict:** code + `{{PRIMARY_CONFIG}}` → Tier 3 deep refs → [AGENTS.md](../AGENTS.md).

---

## Agent task router

Use this table first, then open the linked deep ref. **Tests** column is the minimum command to run after edits (not exhaustive).

| Task | Read first | May also read | Tests |
| --- | --- | --- | --- |
| Change core application logic | [CORE.md](CORE.md) | [ARCHITECTURE.md](ARCHITECTURE.md) | `{{DEFAULT_TEST_COMMAND}}` |
| Change config / env | [CONFIG.md](CONFIG.md) | [SETUP.md](SETUP.md) | — |
| Change schemas / persistence | [DATA_MODEL.md](DATA_MODEL.md) | [CORE.md](CORE.md) | — |
| Change CLI / scripts | [CLI.md](CLI.md) | [CONFIG.md](CONFIG.md) | — |
| Ops symptom | [OPERATIONS.md](OPERATIONS.md) | [FINDINGS.md](FINDINGS.md) | — |
| What to build next | [BACKLOG.md](BACKLOG.md) | [FINDINGS.md](FINDINGS.md) | — |
| New subsystem | [SUBSYSTEM_TEMPLATE.md](SUBSYSTEM_TEMPLATE.md) | [MODULE_ONBOARDING.md](MODULE_ONBOARDING.md) | `pytest tests/test_docs_integrity.py -q` |
| Doc vs code drift | [FINDINGS.md](FINDINGS.md) | `python3 scripts/docs_integrity.py` | `pytest tests/test_docs_integrity.py -q` |

<!-- register_subsystem.py appends router rows -->

---

## Tier 1 — Getting started

| Doc | What it answers |
| --- | --- |
| [../README.md](../README.md) | What is this, how do I run it? |
| [SETUP.md](SETUP.md) | Install, keys, local dev |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Modules, processes, data flow |
| [CLI.md](CLI.md) | Commands, flags, exit codes |

## Tier 2 — Operate

| Doc | What it answers |
| --- | --- |
| [OPERATIONS.md](OPERATIONS.md) | Symptom-first runbook |
| [CONFIG.md](CONFIG.md) | Every tunable |
| [BACKLOG.md](BACKLOG.md) | Unified work portfolio |
| [FINDINGS.md](FINDINGS.md) | Live `F-###` triage |

## Tier 3 — Subsystem deep refs

One file per major subsystem. Canonical source — if AGENTS.md contradicts these, **these win** unless code says otherwise.

| Doc | Subsystem |
| --- | --- |
| [CORE.md](CORE.md) | Core application under `{{SRC_ROOT}}` |

<!-- register_subsystem.py appends tier-3 rows -->

## Tier 4 — Research / design (optional)

RFCs, spikes, experiments — not runtime truth unless code matches. Add files as needed; link from BACKLOG.

## Tier 5 — Meta

| Doc | What it answers |
| --- | --- |
| [SUBSYSTEM_TEMPLATE.md](SUBSYSTEM_TEMPLATE.md) | Required skeleton for new subsystem deep refs |
| [MODULE_ONBOARDING.md](MODULE_ONBOARDING.md) | Module integration gate |
| [proposals/README.md](proposals/README.md) | Deferred plan follow-ups |
| [../AGENTS.md](../AGENTS.md) | Documentation contract, ownership map |

---

## How the tiers fit together

```
Getting Started  →  Operate  →  Deep Refs  →  Research (optional)
     (Tier 1)        (Tier 2)     (Tier 3)         (Tier 4)
                           Meta (Tier 5) governs all tiers
```

---

## Conventions inside every deep ref

- YAML front matter or header: `Last reconciled: YYYY-MM-DD`, `Scope: …`
- **Changelog** section at bottom — append on every behavior change
- Clickable path links to source files
- No marketing copy; verifiable from code
- **Same commit:** behavior change + doc delta together

After markdown edits:

```bash
python3 scripts/docs_integrity.py
python3 -m pytest tests/test_docs_integrity.py -q
```

---

## Where should this go?

| I'm documenting… | Put it in |
| --- | --- |
| New subsystem | `docs/<NAME>.md` + AGENTS.md rows (`register_subsystem.py`) |
| Change inside existing subsystem | That doc's changelog |
| Bug found, can't fix yet | [FINDINGS.md](FINDINGS.md) + link from [BACKLOG.md](BACKLOG.md) |
| Idea / roadmap | [BACKLOG.md](BACKLOG.md) (`BL-###`) |
| Deferred from a plan | [proposals/](proposals/) |
| Operational symptom + fix | [OPERATIONS.md](OPERATIONS.md) |
| Frozen audit/review | [../__ARCHIVE/](../__ARCHIVE/) |

---

## Changelog (index)

- **{{DATE}}** — Initial agent-memory scaffold bootstrap.
