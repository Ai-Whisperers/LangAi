# Company Researcher - Makefile
# Build, test, and deployment automation

.PHONY: help install dev test lint format security build deploy clean

# Default target
help:
	@echo "Company Researcher - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install production dependencies"
	@echo "  make dev         - Install development dependencies"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Run linters"
	@echo "  make format      - Format code"
	@echo "  make security    - Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  make build       - Build Docker image"
	@echo "  make up          - Start Docker Compose stack"
	@echo "  make down        - Stop Docker Compose stack"
	@echo "  make logs        - View container logs"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-staging    - Deploy to staging"
	@echo "  make deploy-prod       - Deploy to production"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make clean-all   - Clean everything including Docker"

# Python version
PYTHON := python3.11
VENV := venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

# Docker settings
IMAGE_NAME := company-researcher
IMAGE_TAG := $(shell git describe --tags --always --dirty)
REGISTRY := ghcr.io/$(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')

#
# Development
#

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev: install
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	pre-commit install

test:
	PYTHONPATH=. $(PYTEST) tests/ -v --cov=src --cov-report=term-missing

test-fast:
	PYTHONPATH=. $(PYTEST) tests/ -v -x --tb=short

test-unit:
	PYTHONPATH=. $(PYTEST) tests/unit/ -v

test-integration:
	PYTHONPATH=. $(PYTEST) tests/integration/ -v

lint:
	$(VENV)/bin/ruff check src/ tests/
	$(VENV)/bin/mypy src/ --ignore-missing-imports

format:
	$(VENV)/bin/black src/ tests/
	$(VENV)/bin/isort src/ tests/
	$(VENV)/bin/ruff check --fix src/ tests/

security:
	$(VENV)/bin/bandit -r src/ -ll
	$(VENV)/bin/safety check -r requirements.txt
	$(VENV)/bin/pip-audit -r requirements.txt

#
# Docker
#

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f deploy/Dockerfile .
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):latest

build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) -f deploy/Dockerfile .

push:
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY):$(IMAGE_TAG)
	docker push $(REGISTRY):$(IMAGE_TAG)

up:
	docker-compose -f deploy/docker-compose.yml up -d

up-build:
	docker-compose -f deploy/docker-compose.yml up -d --build

down:
	docker-compose -f deploy/docker-compose.yml down

logs:
	docker-compose -f deploy/docker-compose.yml logs -f

logs-app:
	docker-compose -f deploy/docker-compose.yml logs -f app

shell:
	docker-compose -f deploy/docker-compose.yml exec app /bin/bash

#
# Deployment
#

deploy-staging:
	@echo "Deploying to staging..."
	kubectl set image deployment/company-researcher app=$(REGISTRY):$(IMAGE_TAG) -n company-researcher-staging
	kubectl rollout status deployment/company-researcher -n company-researcher-staging

deploy-prod:
	@echo "Deploying to production..."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	kubectl set image deployment/company-researcher app=$(REGISTRY):$(IMAGE_TAG) -n company-researcher
	kubectl rollout status deployment/company-researcher -n company-researcher

rollback-staging:
	kubectl rollout undo deployment/company-researcher -n company-researcher-staging

rollback-prod:
	kubectl rollout undo deployment/company-researcher -n company-researcher

#
# Database/Redis
#

redis-cli:
	docker-compose -f deploy/docker-compose.yml exec redis redis-cli

flush-cache:
	docker-compose -f deploy/docker-compose.yml exec redis redis-cli FLUSHALL

#
# Cleanup
#

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .eggs/

clean-all: clean down
	docker system prune -f
	docker volume prune -f
	rm -rf $(VENV)

#
# Documentation
#

docs:
	$(VENV)/bin/mkdocs build

docs-serve:
	$(VENV)/bin/mkdocs serve

#
# Misc
#

version:
	@echo $(IMAGE_TAG)

check: lint test security
	@echo "All checks passed!"
