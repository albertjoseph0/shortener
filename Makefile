.PHONY: help install dev test clean build up down logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt
	cd frontend && npm install

dev: ## Start development environment
	docker-compose up -d db redis
	sleep 5
	alembic upgrade head
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest tests/ -v
	cd frontend && npm test

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

migrate: ## Run database migrations
	alembic upgrade head

migration: ## Create new migration
	alembic revision --autogenerate -m "$(MSG)"

format: ## Format code
	black app/ tests/
	isort app/ tests/
	cd frontend && npm run format

lint: ## Lint code
	flake8 app/ tests/
	cd frontend && npm run lint

prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d