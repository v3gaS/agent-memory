# {{PROJECT_NAME}}

{{STACK_SUMMARY}}

## Quick start

See [docs/SETUP.md](docs/SETUP.md).

## Documentation

| Doc | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Agent index — ownership map, test rules |
| [docs/README.md](docs/README.md) | Task router — read X, run test Y |
| [docs/BACKLOG.md](docs/BACKLOG.md) | What to build next |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Symptom runbook |

**Tests:** never weaken assertions to green CI — see [AGENTS.md](AGENTS.md).

## Run tests

```bash
{{DEFAULT_TEST_COMMAND}}
python3 scripts/docs_integrity.py
python3 -m pytest tests/test_docs_integrity.py -q
```
