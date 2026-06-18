---
Last reconciled: {{DATE}}
Scope: External API inventory — promote at maturity L4.
---

# API_CATALOG — {{PROJECT_NAME}}

> **Optional until L4.** List every external HTTP/RPC endpoint the project calls.

---

## 1. Standing notes

- Verify against vendor docs before changing clients.
- Pair changes with subsystem deep ref + this catalog in the **same commit**.
- Never weaken contract tests to match a broken client.

---

## 2. Endpoints

| Service | Method | Path | Used by | Deep ref |
| --- | --- | --- | --- | --- |
| TODO | GET | /example | core | [CORE.md](CORE.md) |

---

## 3. curl cookbook

```bash
# TODO
curl -sS "https://api.example.com/health"
```

---

## 4. Changelog

- **{{DATE}}** — Stub created; populate at L4.
