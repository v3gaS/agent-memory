---
Last reconciled: {{DATE}}
Scope: Install, environment, and local development.
---

# SETUP — {{PROJECT_NAME}}

---

## 1. Prerequisites

TODO: Language runtime, package manager, database, Docker, etc.

---

## 2. Clone and install

```bash
# TODO: replace with your project commands
git clone <repo-url>
cd <repo>
# e.g. pip install -e ".[dev]"  OR  npm install  OR  cargo build
```

---

## 3. Configuration

Copy env example and edit:

```bash
# TODO: cp .env.example .env  OR  cp config/settings.example.yaml config/settings.yaml
```

Authoritative key list: [CONFIG.md](CONFIG.md).

---

## 4. Run locally

```bash
# TODO: dev server / main entry
{{DEFAULT_TEST_COMMAND}}
```

---

## 5. Verify install

```bash
python3 scripts/docs_integrity.py
python3 -m pytest tests/test_docs_integrity.py -q
```

---

## 6. Changelog

- **{{DATE}}** — Initial setup stub.
