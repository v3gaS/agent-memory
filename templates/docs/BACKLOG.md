---
Last reconciled: {{DATE}}
Scope: Unified work portfolio — not runtime truth.
---

# BACKLOG — Unified work portfolio

> **Start here** when asking "what should we build or fix next?"
>
> Rank and link here; detailed rationale stays in sources (`F-###`, deep refs, proposals).

**Last portfolio pass:** {{DATE}}.

---

## 1. How this fits the doc system

| Layer | File | Role |
| --- | --- | --- |
| Portfolio | BACKLOG.md (this file) | Now / Next / Later, lanes |
| Triage detail | [FINDINGS.md](FINDINGS.md) | Open `F-###` engineering items |
| Runtime truth | code + `{{PRIMARY_CONFIG}}` | Authoritative behavior |
| Subsystem detail | [docs/*.md](README.md) | Deep refs |

---

## 2. Workflow — add, triage, ship

1. New idea → assign `BL-###`, pick lane, set status.
2. Bug → `F-###` in FINDINGS + BACKLOG row with **Source** link.
3. Ship → mark Done, link deep-ref changelog; remove from FINDINGS if resolved.

---

## 3. Status legend

| Status | Meaning |
| --- | --- |
| **Now** | Active or next up |
| **Next** | Queued |
| **Later** | Valid, not scheduled |
| **Done** | Shipped — link changelog |

---

## 4. Now / Next / Later

### Now

| ID | Title | Source | Notes |
| --- | --- | --- | --- |
| BL-001 | Complete ARCHITECTURE + CORE deep refs | bootstrap | Agent-memory scaffold |

### Next

| ID | Title | Source |
| --- | --- | --- |
| BL-002 | Wire doc integrity into CI | bootstrap |

### Later

| ID | Title | Source |
| --- | --- | --- |
| | | |

---

## 5. Lanes

Use lanes to group work; add/remove as the project evolves.

| Lane | Purpose |
| --- | --- |
| **A — Product** | Features, UX |
| **B — Ops / reliability** | Incidents, deploy, observability |
| **C — Engineering** | FINDINGS-driven fixes |
| **D — Subsystem follow-ons** | Deferred from shipped work → [proposals/](proposals/) |

---

## 6. Changelog

- **{{DATE}}** — Initial backlog (agent-memory bootstrap).
