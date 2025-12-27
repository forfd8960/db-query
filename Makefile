.PHONY: help install dev backend frontend backend-install frontend-install test lint format clean build check

# Default target
help:
	@echo "Available commands:"
	@echo "  make install          - Install all dependencies (backend + frontend)"
	@echo "  make dev              - Start both backend and frontend servers"
	@echo "  make backend          - Start backend server only"
	@echo "  make frontend         - Start frontend dev server only"
	@echo "  make backend-install  - Install backend dependencies"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Lint all code"
	@echo "  make format           - Format all code"
	@echo "  make check            - Run type checking"
	@echo "  make build            - Build production artifacts"
	@echo "  make clean            - Remove build artifacts and caches"

# Installation targets
install: backend-install frontend-install
	@echo "✅ All dependencies installed"

backend-install:
	@echo "📦 Installing backend dependencies..."
	@cd backend && ../.venv/bin/python -m pip install -e .

frontend-install:
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install

# Development servers
dev:
	@echo "🚀 Starting backend and frontend..."
	@make -j 2 backend frontend

backend:
	@echo "🐍 Starting backend server on http://127.0.0.1:8000"
	@cd backend && ../.venv/bin/python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@echo "⚛️  Starting frontend dev server on http://localhost:5173"
	@cd frontend && npm run dev

# Testing
test: test-backend test-frontend

test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && ../.venv/bin/python -m pytest tests/ -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm run test

# Linting
lint: lint-backend lint-frontend

lint-backend:
	@echo "🔍 Linting backend code..."
	@cd backend && ../.venv/bin/python -m ruff check src/

lint-frontend:
	@echo "🔍 Linting frontend code..."
	@cd frontend && npm run lint

# Formatting
format: format-backend format-frontend

format-backend:
	@echo "✨ Formatting backend code..."
	@cd backend && ../.venv/bin/python -m ruff format src/

format-frontend:
	@echo "✨ Formatting frontend code..."
	@cd frontend && npm run format || echo "No format script defined"

# Type checking
check: check-backend check-frontend

check-backend:
	@echo "🔎 Type checking backend..."
	@cd backend && ../.venv/bin/python -m mypy src/

check-frontend:
	@echo "🔎 Type checking frontend..."
	@cd frontend && npm run build

# Building
build: build-backend build-frontend

build-backend:
	@echo "🏗️  Building backend..."
	@cd backend && ../.venv/bin/python -m pip install build && ../.venv/bin/python -m build

build-frontend:
	@echo "🏗️  Building frontend..."
	@cd frontend && npm run build

# Database
db-init:
	@echo "🗄️  Initializing SQLite database..."
	@.venv/bin/python -c "import sys; sys.path.insert(0, 'backend/src'); from services.storage import init_database; init_database(); print('✅ Database initialized')"

db-reset:
	@echo "⚠️  Resetting database..."
	@rm -f db-query/db_query.db
	@make db-init

# Cleaning
clean: clean-backend clean-frontend clean-db

clean-backend:
	@echo "🧹 Cleaning backend artifacts..."
	@cd backend && rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	@find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-frontend:
	@echo "🧹 Cleaning frontend artifacts..."
	@cd frontend && rm -rf dist/ node_modules/.vite

clean-db:
	@echo "🧹 Cleaning database..."
	@rm -f db-query/db_query.db

# Setup venv (if needed)
venv:
	@echo "🐍 Creating virtual environment..."
	@python3.11 -m venv .venv
	@.venv/bin/python -m pip install --upgrade pip
	@echo "✅ Virtual environment created. Run: source .venv/bin/activate"

# Health check
health:
	@echo "🏥 Checking backend health..."
	@curl -s http://127.0.0.1:8000/health && echo "\n✅ Backend is healthy" || echo "\n❌ Backend is not running"

# Quick start (install + dev)
start: install dev
