CODESPELL_DIRS ?= blockbuilder/ examples/
CODESPELL_SKIP ?= "*.pyc"

all: doctest

doctest: codespell pydocstyle

codespell:
	@echo "Run codespell"
	@codespell $(CODESPELL_DIRS) -S $(CODESPELL_SKIP)

pydocstyle:
	@echo "Run pydocstyle"
	@pydocstyle blockbuilder

tests:
	@echo "Run tests"
	@pytest -v blockbuilder -n 1

coverage:
	@echo "Run coverage"
	@pytest --cov=blockbuilder -n 1

coverage-html: coverage
	@echo "Report HTML coverage"
	@coverage html

coverage-codacy: coverage
	@echo "Report XML coverage"
	@coverage xml -o cobertura.xml
