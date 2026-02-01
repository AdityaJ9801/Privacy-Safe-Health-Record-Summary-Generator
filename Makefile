.PHONY: help install dev-install run test clean docker-build docker-run format lint

help:
	@echo "Medical Report Analysis API - Available Commands"
	@echo "================================================"
	@echo "install          - Install production dependencies"
	@echo "dev-install      - Install development dependencies"
	@echo "run              - Run the API server"
	@echo "test             - Run tests"
	@echo "test-cov         - Run tests with coverage"
	@echo "clean            - Clean up cache and temporary files"
	@echo "docker-build     - Build Docker image"
	@echo "docker-run       - Run with Docker Compose"
	@echo "docker-stop      - Stop Docker containers"
	@echo "format           - Format code with black"
	@echo "lint             - Lint code with ruff"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black ruff

run:
	python run.py

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov

docker-build:
	docker build -t medical-report-api .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

format:
	black app/ tests/ --line-length 100

lint:
	ruff check app/ tests/

