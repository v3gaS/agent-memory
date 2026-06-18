# Archive — frozen snapshots

Point-in-time artifacts that should **not** drift with live docs:

- Code review outputs (`REVIEW-YYYY-MM-DD/`)
- Audit findings (`audit-YYYY-MM-DD/FINDINGS.md`)
- Incident postmortems
- Superseded full FINDINGS exports

**Live triage** stays in [docs/FINDINGS.md](../docs/FINDINGS.md). **Portfolio** stays in [docs/BACKLOG.md](../docs/BACKLOG.md).

When archiving:

1. Create dated folder `__ARCHIVE/<name>-YYYY-MM-DD/`
2. Add `status.txt` (`COMPLETE` / `SUPERSEDED`)
3. Link from BACKLOG or FINDINGS — do not duplicate active work here

## Changelog

- **{{DATE}}** — Archive root created (agent-memory bootstrap).
