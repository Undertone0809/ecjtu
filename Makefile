#* Variables
SHELL := /usr/bin/env bash

#* Docker variables
IMAGE := ecjtu
VERSION := latest

install:
	poetry install --sync

lock:
	poetry lock

pre-commit-install:
	poetry run pre-commit install --install-hooks

polish-codestyle:
	poetry run ruff format --config pyproject.toml .
	poetry run ruff check --fix --config pyproject.toml .

format: polish-codestyle
formatting: polish-codestyle

test:
	poetry run pytest

coverage-badge:
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
	@echo "lock: Refresh the Poetry lock file"
	@echo "pre-commit-install: Install pre-commit hooks"
	@echo "polish-codestyle: Format code"
	@echo "format: Format code"
	@echo "formatting: Format code"
	@echo "test: Run tests"
	@echo "coverage-badge: Refresh the coverage badge"
	@echo "check-codestyle: Check code style"
	@echo "lint: Run tests and check code style"
	@echo "lint-fix: Fix code style"
	@echo "docker-build: Build docker image"
	@echo "docker-remove: Remove docker image"
	@echo "pycache-remove: Remove pycache"
	@echo "dsstore-remove: Remove .DS_Store"
	@echo "mypycache-remove: Remove mypy cache"
	@echo "ipynbcheckpoints-remove: Remove .ipynb_checkpoints"
	@echo "pytestcache-remove: Remove .pytest_cache"
	@echo "build-remove: Remove build directory"
	@echo "cleanup: Remove all cache files"
	@echo "help: Show this help message"

.PHONY: install lock pre-commit-install polish-codestyle format formatting test coverage-badge check-codestyle lint lint-fix docker-build docker-remove pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove build-remove cleanup help
