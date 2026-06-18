# Proposals — deferred work by subsystem

Open follow-ups and design-only specs live here after a wave ships. **Runtime authority** remains code + `{{PRIMARY_CONFIG}}` → subsystem deep refs in [`docs/`](../README.md).

## Index

| Subsystem | Proposal file | Deep ref | Backlog |
| --- | --- | --- | --- |
| General | [GENERAL.md](GENERAL.md) | — | — |

Add a row per subsystem as the project grows. Split `GENERAL.md` when a subsystem accumulates 3+ deferred sections.

## Discipline

When a plan lists **Out of scope** or **Possible follow-ups**:

1. Append to the matching proposal file in the **same commit** as implementation (or when finalizing a deferred plan).
2. Set `status: Proposed | Partial | Shipped` on the section you touch.
3. When fully shipped, **remove** the section from this folder and record in the deep ref changelog.
4. Cross-link [`BACKLOG.md`](../BACKLOG.md) when a `BL-###` item tracks the work.

Do not leave deferred items only in `.cursor/plans/` — those are ephemeral.

## Section template

```markdown
## <Title> (BL-### optional)

status: Proposed

Context: …

Out of scope because: …

Suggested approach: …

Tests to add: …
```

## Changelog

- **{{DATE}}** — Initial proposals index (agent-memory bootstrap).
