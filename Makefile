PYTHON ?= python
CODESPELL_DIRS ?= blockbuilder/
CODESPELL_SKIP ?= "*.pyc"

all: doctest

style: flake8 codespell pydocstyle

pip:
	@echo "Check pip version"
	@which pip
	@pip --version

install: pip
	@echo "Run pip install -e ."
	@pip install -e .

archive:
	@echo "Create archive"
	@git archive HEAD --format=zip > archive.zip

flake8:
	@echo "Run flake8"
	@flake8 --count blockbuilder setup.py

codespell:
	@echo "Run codespell"
	@codespell $(CODESPELL_DIRS) -S $(CODESPELL_SKIP)

pydocstyle:
	@echo "Run pydocstyle"
	@pydocstyle blockbuilder

wheel:
	@echo "Build wheel"
	$(PYTHON) setup.py sdist bdist_wheel

tests:
	@echo "Run tests"
	@pytest -v blockbuilder

coverage:
	@echo "Run coverage"
	@pytest --cov=blockbuilder

coverage-html: coverage
	@echo "Report HTML coverage"
	@coverage html

coverage-codacy: coverage
	@echo "Report XML coverage"
	@coverage xml -o cobertura.xml
