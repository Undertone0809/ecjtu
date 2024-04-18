#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
OS := $(shell python -c "import sys; print(sys.platform)")

ifeq ($(OS),win32)
	PYTHONPATH := $(shell python -c "import os; print(os.getcwd())")
    TEST_COMMAND := set PYTHONPATH=$(PYTHONPATH) && poetry run pytest -c pyproject.toml --cov-report=html --cov=ecjtu tests/
else
	PYTHONPATH := `pwd`
    TEST_COMMAND := PYTHONPATH=$(PYTHONPATH) poetry run pytest -c pyproject.toml --cov-report=html --cov=ecjtu tests/
endif


#* Docker variables
IMAGE := ecjtu
VERSION := latest

install:
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n

pre-commit-install:
	poetry run pre-commit install

polish-codestyle:
	poetry run ruff format --config pyproject.toml .
	poetry run ruff check --fix --config pyproject.toml .

format: polish-codestyle
formatting: polish-codestyle

test:
	$(TEST_COMMAND)
	poetry run coverage-badge -o assets/images/coverage.svg -f

check-codestyle:
	poetry run ruff format --check --config pyproject.toml .
	poetry run ruff check --config pyproject.toml .

lint: test check-codestyle 

lint-fix: polish-codestyle

docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

build-remove:
	rm -rf build/

cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove

help:
	@echo "install: Install dependencies"
	@echo "pre-commit-install: Install pre-commit hooks"
	@echo "polish-codestyle: Format code"
	@echo "format: Format code"
	@echo "formatting: Format code"
	@echo "test: Run tests"
	@echo "check-codestyle: Check code style"
	@echo "lint: Run tests and check code style"
	@echo "lint-fix: Fix code style"
	@echo "docker-build: Build docker image"
	@echo "docker-remove: Remove docker image"
	@echo "pycache-remove: Remove pycache"
	@echo "dsstore-remove: Remove .DS_Store"
	@echo "mypycache-remove: Remove mypy cache"
	@echo "ipynbcheckpoints-remove: Remove ipynb checkpoints"
	@echo "pytestcache-remove: Remove pytest cache"
	@echo "build-remove: Remove build directory"
	@echo "cleanup: Remove all cache files"
	@echo "help: Show this help message"


.PHONY: install pre-commit-install polish-codestyle format formatting test check-codestyle lint lint-fix docker-build docker-remove pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove build-remove cleanup help