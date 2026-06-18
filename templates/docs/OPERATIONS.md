---
Last reconciled: {{DATE}}
Scope: Symptom-first operational runbook.
---

# OPERATIONS — {{PROJECT_NAME}}

Symptom → diagnose → fix. For portfolio prioritization see [BACKLOG.md](BACKLOG.md).

---

## 1. App won't start / build fails

**Symptoms:** process exits immediately, compile error, missing module.

**Diagnose:**

```bash
# TODO: your build/run command with verbose flags
{{DEFAULT_TEST_COMMAND}}
```

**Common causes:**

- Missing env / config — see [SETUP.md](SETUP.md), [CONFIG.md](CONFIG.md)
- Dependency not installed
- Wrong runtime version

**Fix:** address root cause; document new symptom here if recurring.

---

## 2. Tests failing

**Symptoms:** CI red, local test failures.

**Diagnose:**

```bash
{{DEFAULT_TEST_COMMAND}}
python3 -m pytest tests/test_docs_integrity.py -q
```

**Rules:**

- **Never weaken tests to pass** — see [AGENTS.md](../AGENTS.md) test discipline.
- Fix code if behavior was wrong; fix test only if specified intent was wrong (document in deep ref).

**Fix:** see linked subsystem deep ref debugging runbook.

---

## 3. Doc vs code drift

**Symptoms:** agent/human docs disagree with runtime.

**Diagnose:**

```bash
python3 scripts/docs_integrity.py
```

**Fix:** update subsystem deep ref in same PR as code; file `F-###` if can't fix immediately.

---

## 4. Performance degradation

TODO: Add project-specific symptoms, queries, profilers.

---

## 5. Production incident template

1. Capture symptom + timestamp
2. Check [FINDINGS.md](FINDINGS.md) for known `F-###`
3. Rollback or hotfix with same-commit doc update
4. Post-incident: archive notes under `__ARCHIVE/incidents-YYYY-MM-DD/` (optional L4)

---

## 6. Changelog

- **{{DATE}}** — Initial operations stub.
