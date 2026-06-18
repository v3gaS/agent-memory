---
Last reconciled: {{DATE}}
Scope: Required skeleton for new subsystem deep refs.
---

# <Subsystem Name> — Full Reference

> Copy to `docs/<SUBSYSTEM>.md` or use `python3 scripts/register_subsystem.py`.
>
> Every new subsystem MUST ship with:
>
> 1. A doc like this (all 20 sections or justified N/A).
> 2. Rows in [AGENTS.md](../AGENTS.md) ownership map, doc map, and subsystem pointers.
> 3. A row in [docs/README.md](README.md) agent task router with a **Tests** command.
>
> See [AGENTS.md Documentation Contract](../AGENTS.md#documentation-contract).

Last updated: YYYY-MM-DD.

---

## Table of contents

1. [Overview](#1-overview)
2. [Data source / inputs](#2-data-source--inputs)
3. [Architecture](#3-architecture)
4. [Data model](#4-data-model)
5. [API surface](#5-api-surface)
6. [Config reference](#6-config-reference)
7. [Runtime flow](#7-runtime-flow)
8. [Integration with other subsystems](#8-integration-with-other-subsystems)
9. [State transitions / lifecycle](#9-state-transitions--lifecycle)
10. [Scheduler / timing](#10-scheduler--timing)
11. [UI surface](#11-ui-surface)
12. [Alerts / notifications](#12-alerts--notifications)
13. [Persistence](#13-persistence)
14. [Research / evaluation](#14-research--evaluation)
15. [Extension hooks](#15-extension-hooks)
16. [Debugging runbook](#16-debugging-runbook)
17. [CLI cookbook](#17-cli-cookbook)
18. [Invariants and safety rules](#18-invariants-and-safety-rules)
19. [Known gotchas](#19-known-gotchas)
20. [Changelog](#20-changelog)

---

## 1. Overview

*One paragraph, ~3 sentences. What this subsystem does and why.*

TODO

---

## 2. Data source / inputs

TODO

---

## 3. Architecture

```mermaid
flowchart LR
    TODO
```

TODO

---

## 4. Data model

Reference [DATA_MODEL.md](DATA_MODEL.md) for shared stores.

TODO

---

## 5. API surface

Source: `{{SRC_ROOT}}<module>` (replace with real path).

TODO: public functions / classes / routes with signatures.

---

## 6. Config reference

Reference [CONFIG.md](CONFIG.md). List subsystem-specific keys.

TODO

---

## 7. Runtime flow

1. TODO
2. TODO

---

## 8. Integration with other subsystems

- **Consumes:** TODO
- **Feeds:** TODO

---

## 9. State transitions / lifecycle

N/A — or TODO.

---

## 10. Scheduler / timing

N/A — or TODO.

---

## 11. UI surface

N/A — or TODO.

---

## 12. Alerts / notifications

N/A — or TODO.

---

## 13. Persistence

TODO or N/A.

---

## 14. Research / evaluation

N/A — or TODO.

---

## 15. Extension hooks

1. TODO
2. Update §5 and AGENTS.md pointer.

---

## 16. Debugging runbook

Minimum 8 symptom-first rows over time; start with 2 at bootstrap.

### 16.1 Symptom: subsystem tests fail

**Diagnose:** run Tests column from [docs/README.md](README.md).

**Fix:** never weaken tests; fix code or documented intent.

### 16.2 TODO

---

## 17. CLI cookbook

```bash
# TODO
{{DEFAULT_TEST_COMMAND}}
```

---

## 18. Invariants and safety rules

1. TODO
2. **Doc discipline.** Same-commit updates to this file + AGENTS.md when behavior changes.
3. **Test discipline.** Never alter tests merely to pass CI.

---

## 19. Known gotchas

- TODO

---

## 20. Changelog

- **YYYY-MM-DD** — Initial ship.
