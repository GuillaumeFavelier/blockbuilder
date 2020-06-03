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

coverage:
	@echo "Run coverage"
	@pytest --cov=blockbuilder -n 1

coverage-report: coverage
	@echo "Report coverage"
	@coverage report

coverage-html: coverage
	@echo "Report HTML coverage"
	@coverage html

coverage-codacy: coverage
	@echo "Report XML coverage"
	@coverage xml -o cobertura.xml
