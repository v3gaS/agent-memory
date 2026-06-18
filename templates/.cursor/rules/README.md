# Cursor rules — domain guardrails

Add `.mdc` files here for **narrow, path-scoped** agent rules. Examples:

| File | globs | Purpose |
| --- | --- | --- |
| `api-vendor.mdc` | `src/integrations/**` | Fetch current vendor docs before changing API clients |
| `ui-design.mdc` | `src/ui/**`, `apps/web/**` | Visual language — behavior still in subsystem deep ref |

**Rule:** `.mdc` files supplement `docs/*.md`; they do not replace deep refs.

## Template (`example-api.mdc`)

```markdown
---
description: Fetch current vendor API docs before editing integration code
globs: src/integrations/**
---

Before changing matched files, read the vendor's current API documentation.
Update the subsystem deep ref in docs/ in the same commit.
Never weaken integration tests to pass — fix client or update documented contract.
```

See [docs/GROWTH.md](../../docs/GROWTH.md) L3→L4 promotion notes when adding rules.
