.PHONY: help install run test lint migrate clean

help: ## Show this help message
	@echo "PatchPanda Gateway - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	poetry install

run: ## Run the development server
	poetry run uvicorn patchpanda.gateway.main:app --host 0.0.0.0 --port 8000 --reload

run-prod: ## Run the production server
	poetry run uvicorn patchpanda.gateway.main:app --host 0.0.0.0 --port 8000

test: ## Run tests
	poetry run pytest tests/ -v

test-coverage: ## Run tests with coverage
	poetry run pytest tests/ --cov=patchpanda.gateway --cov-report=html --cov-report=term

lint: ## Run linting and formatting
	poetry run black src/ tests/
	poetry run isort src/ tests/
	poetry run flake8 src/ tests/
	poetry run mypy src/

lint-check: ## Check linting without making changes
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/
	poetry run flake8 src/ tests/
	poetry run mypy src/

migrate: ## Run database migrations
	poetry run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create name=migration_name)
	poetry run alembic revision --autogenerate -m "$(name)"

migrate-downgrade: ## Downgrade database (usage: make migrate-downgrade revision=revision_id)
	poetry run alembic downgrade $(revision)

migrate-history: ## Show migration history
	poetry run alembic history

db-init: ## Initialize database tables
	poetry run python -c "from patchpanda.gateway.db.base import init_db; init_db()"

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

docker-build: ## Build Docker image
	docker build -t patchpanda-gateway .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env patchpanda-gateway

docker-clean: ## Clean Docker images and containers
	docker system prune -f
	docker image prune -f
