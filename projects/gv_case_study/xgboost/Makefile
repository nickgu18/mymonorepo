PYTHON ?= python3
VENV_DIR ?= .venv

.PHONY: venv install test

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -e .[dev]

test:
	. $(VENV_DIR)/bin/activate && pytest

