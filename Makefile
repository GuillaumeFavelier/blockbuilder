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
	@coverage run -m pytest -v blockbuilder

coverage-report:
	@echo "Report coverage"
	@coverage report

coverage-html:
	@echo "Report HTML coverage"
	@coverage html

coverage-codacy:
	@echo "Report XML coverage"
	@coverage xml -o cobertura.xml
