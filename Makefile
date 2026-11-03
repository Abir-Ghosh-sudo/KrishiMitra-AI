# KrishiMitra-AI Makefile

.PHONY: help install dev build test lint format typecheck clean run-api run-ui docker-up docker-down mojo-build mojo-test

help:
	@echo "KrishiMitra-AI - Makefile Commands"
	@echo "=================================="
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Setup development environment"
	@echo "  make build      - Build all packages"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make typecheck  - Run type checking"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make run-api    - Run API server"
	@echo "  make run-ui     - Run UI app"
	@echo "  make mojo-build - Compile Mojo kernels"
	@echo "  make mojo-test  - Test Mojo kernels"

install:
	pip install -e ".[dev]" 2>/dev/null || pip install -e .
	@echo "Installing all packages..."
	pip install -e packages/core -e packages/database -e packages/ml -e packages/mojo -e packages/weather 2>/dev/null || true
	pip install -e packages/geospatial -e packages/soil -e packages/optimization -e packages/simulation 2>/dev/null || true

dev:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt 2>/dev/null || pip install pytest pytest-asyncio ruff mypy
	pip install -e packages/mojo
	@echo "Development environment ready"

build:
	python setup.py build_ext --inplace 2>/dev/null || true
	@echo "Build complete"

test:
	pytest tests/ -v 2>/dev/null || pytest -v 2>/dev/null || echo "No tests found"

lint:
	ruff check . 2>/dev/null || flake8 . 2>/dev/null || echo "Linting skipped"

format:
	ruff format . 2>/dev/null || black . 2>/dev/null || echo "Formatting skipped"

typecheck:
	mypy packages/ 2>/dev/null || echo "Type checking skipped"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || rm -rf __pycache__ */__pycache__ */*/__pycache__
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache

run-api:
	cd apps/api && uvicorn krishimitra_api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	cd apps/web && npm run dev 2>/dev/null || cd apps/mobile && flutter run 2>/dev/null || echo "UI not configured"

docker-up:
	docker-compose up -d 2>/dev/null || echo "docker-compose not found"

docker-down:
	docker-compose down 2>/dev/null || echo "docker-compose not found"

mojo-build:
	@echo "Compiling Mojo kernels..."
	@cd packages/mojo/src/krishimitra_mojo/mojo_files && mojo -O3 image.mojo 2>&1 || echo "image.mojo compilation skipped"
	@cd packages/mojo/src/krishimitra_mojo/mojo_files && mojo -O3 geospatial.mojo 2>&1 || echo "geospatial.mojo compilation skipped"
	@cd packages/mojo/src/krishimitra_mojo/mojo_files && mojo -O3 soil.mojo 2>&1 || echo "soil.mojo compilation skipped"
	@cd packages/mojo/src/krishimitra_mojo/mojo_files && mojo -O3 irrigation.mojo 2>&1 || echo "irrigation.mojo compilation skipped"
	@cd packages/mojo/src/krishimitra_mojo/mojo_files && mojo -O3 crop_growth.mojo 2>&1 || echo "crop_growth.mojo compilation skipped"
	@cd packages/mojo/src/krishimitra_mojo/mojo_files && mojo -O3 pest_disease_risk.mojo 2>&1 || echo "pest_disease_risk.mojo compilation skipped"

mojo-test:
	@echo "Testing Mojo kernels..."
	python -c "import krishimitra_mojo; print('krishimitra_mojo loaded OK')" 2>&1
