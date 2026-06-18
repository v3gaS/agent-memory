# Publish `agent-memory` as a standalone GitHub template repository

This folder (`scaffold/agent-memory/`) is the **source of truth** inside Stock Scanner.
Follow these steps once to publish a public (or private) template others can install with
`curl`, `degit`, or `gh repo create --template`.

---

## 1. Export a clean standalone tree

From the Stock Scanner repo root:

```bash
chmod +x scaffold/agent-memory/scripts/export-standalone.sh
./scaffold/agent-memory/scripts/export-standalone.sh ../agent-memory
```

Or from inside this directory:

```bash
make export DEST=../agent-memory
```

---

## 2. Configure install URL

Edit **`config/install.defaults.env`** in the exported repo:

```env
AGENT_MEMORY_INSTALL_REPO=https://github.com/YOUR_ORG/agent-memory.git
AGENT_MEMORY_INSTALL_REF=main
```

Replace `YOUR_ORG` everywhere:

- `config/install.defaults.env`
- `README.md` curl examples
- `install.ps1` default repo (via env file)
- Search: `YOUR_ORG` in the exported tree

```bash
cd ../agent-memory
grep -r YOUR_ORG . --exclude-dir=.git
```

---

## 3. Initialize git and push

```bash
cd ../agent-memory
git init
git add .
git commit -m "Initial agent-memory template v$(cat VERSION)"
gh repo create YOUR_ORG/agent-memory --public --source=. --push
```

Or create the repo in GitHub UI, then:

```bash
git remote add origin git@github.com:YOUR_ORG/agent-memory.git
git push -u origin main
```

Or use the automated helper (requires `gh` CLI, replaces `YOUR_ORG` in exported tree):

```bash
chmod +x scripts/publish-github.sh
./scripts/publish-github.sh YOUR_ORG/agent-memory ../agent-memory
```

---

## 4. Mark as GitHub template

GitHub → **Settings** → **General** → check **Template repository**.

Users can then:

```bash
gh repo create my-app --template YOUR_ORG/agent-memory --private
# Then in my-app: ./install.sh --local --target .  (if template files are the installer only)
```

**Note:** The template repo is the **installer/tooling** repo. Running `install.sh --target`
copies the doc scaffold into the user's actual application repo — not the template itself.

---

## 5. Verify standalone CI

The exported repo includes `.github/workflows/ci.yml`. After push, confirm GitHub Actions is green.

Local self-check before push:

```bash
./install.sh --local --target /tmp/am-smoke --yes --preset python --project-name Smoke
```

---

## 6. Release tags (optional)

Tag releases so `--ref v0.1.0` pins installs:

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

Users:

```bash
AGENT_MEMORY_INSTALL_REF=v0.1.0 curl -fsSL .../install.sh | bash -s -- --target .
```

---

## 7. Sync updates from Stock Scanner

When you improve the scaffold in Stock Scanner:

```bash
# Re-export
./scaffold/agent-memory/scripts/export-standalone.sh ../agent-memory

# In standalone repo — review diff, bump VERSION, commit
cd ../agent-memory
git diff
# merge manually if standalone repo has diverged (org-specific README badges, etc.)
```

Keep Stock Scanner's `tests/test_agent_memory_scaffold.py` green after scaffold changes.

---

## Install methods summary

| Method | Command |
| --- | --- |
| **curl (remote)** | `curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/agent-memory/main/install.sh \| bash -s -- --target .` |
| **clone + local** | `git clone .../agent-memory.git && cd agent-memory && ./install.sh --local --target /path/to/app` |
| **degit** | `npx degit YOUR_ORG/agent-memory /tmp/am && /tmp/am/install.sh --local --target .` |
| **make** | `make install TARGET=../my-app` |
| **PowerShell** | `.\install.ps1 -Target C:\dev\my-app -Yes -Preset node -ProjectName MyApp` |
| **apply only** | `python3 apply.py --target /path/to/app` |

---

## Copier (optional)

For teams using [Copier](https://copier.readthedocs.io/):

```bash
pip install copier
copier copy https://github.com/YOUR_ORG/agent-memory /path/to/new-project
cd /path/to/new-project
./install.sh --local --target .
```

See `copier.yml` in this repo.

---

## Changelog

- **2026-06-18** — Initial publish guide for standalone template repository.
