CODESPELL_DIRS ?= blockbuilder/ examples/
CODESPELL_SKIP ?= "*.pyc"

all: doctest

doctest: codespell pydocstyle

codespell:
	@echo "Running codespell"
	@codespell $(CODESPELL_DIRS) -S $(CODESPELL_SKIP)

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle blockbuilder
