.PHONY: help install test verify export version

# Default target project (override: make install TARGET=../my-app)
TARGET ?= ..
SCAFFOLD := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
EXPORT_DEST ?= $(SCAFFOLD)export/agent-memory-standalone

help:
	@echo "agent-memory template repo"
	@echo ""
	@echo "  make install TARGET=../my-app     Run install.sh --local"
	@echo "  make test                         Self-test template (pytest in parent or here)"
	@echo "  make verify TARGET=../my-app      Docs integrity on bootstrapped project"
	@echo "  make export DEST=../agent-memory  Export standalone git repo folder"
	@echo "  make version                      Print VERSION"

install:
	@chmod +x "$(SCAFFOLD)install.sh" "$(SCAFFOLD)bin/agent-memory"
	@"$(SCAFFOLD)install.sh" --local --target "$(abspath $(TARGET))"

test:
	@python3 -m pytest "$(SCAFFOLD)../tests/test_agent_memory_scaffold.py" -q 2>/dev/null || \
	 python3 -m pytest tests/test_template_repo.py -q

verify:
	@cd "$(abspath $(TARGET))" && python3 scripts/docs_integrity.py
	@cd "$(abspath $(TARGET))" && python3 -m pytest tests/test_docs_integrity.py -q

export:
	@chmod +x "$(SCAFFOLD)scripts/export-standalone.sh"
	@"$(SCAFFOLD)scripts/export-standalone.sh" "$(abspath $(EXPORT_DEST))"

version:
	@cat "$(SCAFFOLD)VERSION"
