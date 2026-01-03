.PHONY: install lint type-check test check

install:
	pip install -e .[dev]

lint:
	ruff check .

type-check:
	mypy .

test:
	pytest

check: lint type-check test
	@echo "All checks passed!"
