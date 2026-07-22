.PHONY: help install uninstall lint test build run verify \
        pdm-install validate-manifests marketplace-add plugin-install

help:
	@echo "Dev Commander - Make targets"
	@echo ""
	@echo "  make install     Install Python deps, validate manifests, register the local"
	@echo "                   marketplace, and install the plugin. Idempotent."
	@echo "  make uninstall   Remove the plugin and unregister the marketplace."
	@echo "  make lint        Run the ruff linter."
	@echo "  make test        Run pytest."
	@echo "  make build       Placeholder; no build artifacts."
	@echo "  make run         Placeholder; no runtime."
	@echo "  make verify      Run lint, test, and the skill verifier."

install: pdm-install validate-manifests marketplace-add plugin-install

uninstall:
	-claude plugin uninstall dev-commander
	-claude plugin marketplace remove dev-commander-marketplace

pdm-install:
	pdm install

validate-manifests:
	claude plugin validate .
	claude plugin validate plugins/dev-commander

marketplace-add:
	@if claude plugin marketplace list 2>/dev/null | grep -q dev-commander-marketplace; then \
		echo "marketplace dev-commander-marketplace already registered"; \
	else \
		claude plugin marketplace add "$$PWD"; \
	fi

plugin-install:
	@if claude plugin list 2>/dev/null | grep -q 'dev-commander@dev-commander-marketplace'; then \
		echo "plugin dev-commander already installed"; \
	else \
		claude plugin install dev-commander@dev-commander-marketplace; \
	fi

lint:
	pdm run ruff check .

test:
	pdm run pytest

build:
	@echo "No build artifacts."

run:
	@echo "No runtime."

verify: lint test
	pdm run python scripts/verify_skills.py
