.PHONY: help install dev test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

dev: ## Start development environment with Docker
	docker-compose up -d

dev-frontend: ## Start frontend only
	cd frontend && npm run dev

dev-backend: ## Start backend only
	cd backend && uvicorn app.main:app --reload

stop: ## Stop all Docker containers
	docker-compose down

test: ## Run all tests
	cd backend && pytest
	cd frontend && npm test

test-backend: ## Run backend tests
	cd backend && pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

lint: ## Run linters
	cd backend && black . && isort . && flake8
	cd frontend && npm run lint

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(name)"

clean: ## Clean build artifacts
	rm -rf frontend/.next frontend/out
	rm -rf backend/__pycache__ backend/.pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

logs: ## Show all logs
	docker-compose logs -f

db-reset: ## Reset database
	docker-compose down -v
	docker-compose up -d postgres
	sleep 3
	cd backend && alembic upgrade head

setup: ## Initial project setup
	chmod +x scripts/*.sh
	./scripts/setup.sh
