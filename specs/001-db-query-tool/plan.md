# Implementation Plan: Database Query Tool

**Branch**: `001-db-query-tool` | **Date**: 2025-12-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-db-query-tool/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a web-based PostgreSQL query tool that allows users to connect to databases, browse schema metadata (tables/views/columns), execute SQL queries with safety validation, and convert natural language to SQL using LLM. The tool enforces read-only access (SELECT only) with automatic LIMIT 1000 for unbounded queries. Metadata is cached locally in SQLite to minimize database overhead. Frontend provides tree-based schema navigation, Monaco SQL editor, and table-based result display. Backend implements REST API with FastAPI, using sqlparse for validation and OpenAI SDK for natural language conversion.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ with strict mode (frontend)  
**Primary Dependencies**: 
- Backend: FastAPI, Pydantic, sqlparse, SQLGlot, OpenAI SDK, psycopg2, SQLite
- Frontend: React 19+, Refine 5, Ant Design, Tailwind CSS 4, Monaco Editor

**Storage**: SQLite (local file at `./db-query/db_query.db` for connection URLs and metadata cache); PostgreSQL (external, user-provided databases for querying)  
**Testing**: pytest (backend), Vitest/React Testing Library (frontend)  
**Target Platform**: Web application (browser + local server), development/internal use on macOS/Linux/Windows  
**Project Type**: Web application (separate backend and frontend)  
**Performance Goals**: 
- Query execution < 5 seconds (excluding database latency)
- Metadata extraction < 30 seconds for typical databases (< 1000 tables)
- UI responsiveness < 100ms for user interactions

**Constraints**: 
- Read-only database access (SELECT only, enforced via sqlparse)
- Auto-LIMIT 1000 for unbounded queries
- CORS enabled for all origins (development tool)
- No authentication (open access)
- OpenAI API key via environment variable (OPENAI_API_KEY)

**Scale/Scope**: 
- Single-user local application
- Support databases with < 1000 tables for optimal performance
- Result sets limited to 1000 rows
- Multiple database connections managed simultaneously

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Strict Type Safety ✅
- Backend: All Python code will use type hints (enforced by mypy in development)
- Frontend: TypeScript strict mode enabled in tsconfig.json
- Pydantic models provide runtime type validation for all API boundaries
- No `any` types in TypeScript without explicit justification

**Status**: PASS - Architecture supports comprehensive type safety

### Principle II: Ergonomic Code Style ✅
- Backend: Ergonomic Python (Pythonic idioms, clear naming, readable structure)
- Frontend: Modern React patterns (functional components, hooks, composition)
- Code structure follows language conventions (REST resources, React component hierarchy)

**Status**: PASS - Design follows language-specific best practices

### Principle III: Data Model Standards ✅
- All API request/response schemas defined as Pydantic models
- Pydantic configured with `alias_generator=to_camel` for camelCase serialization
- Validation rules embedded in models (URL validation, SQL statement type checking)

**Status**: PASS - Pydantic models with camelCase enforced at serialization layer

### Principle IV: API Conventions ✅
- REST endpoints follow resource naming conventions (`/api/v1/databases/`)
- JSON responses with camelCase keys (via Pydantic)
- HTTP status codes: 200 (success), 400 (validation), 404 (not found), 500 (server error)
- Structured error responses with `message`, `code`, and `details` fields

**Status**: PASS - REST/JSON conventions fully adopted

### Principle V: Open Access ✅
- No authentication middleware in FastAPI
- No user session management
- CORS configured to accept all origins
- Documentation explicitly states "development/internal tool" limitation

**Status**: PASS - No auth implementation as specified

### Overall Gate Result: ✅ PASS

All constitution principles satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-db-query-tool/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.yaml        # OpenAPI specification
├── checklists/          # Quality validation
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS config
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── database.py         # Database connection models
│   │   ├── metadata.py         # Table/column metadata models
│   │   ├── query.py            # Query request/response models
│   │   └── errors.py           # Error response models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── db_connection.py    # PostgreSQL connection management
│   │   ├── metadata_extractor.py  # Schema metadata extraction
│   │   ├── query_executor.py   # SQL validation & execution
│   │   ├── nl_converter.py     # Natural language to SQL (LLM)
│   │   └── storage.py          # SQLite persistence
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── databases.py    # Database CRUD endpoints
│   │   │   └── queries.py      # Query execution endpoints
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── sql_validator.py    # sqlparse integration
│       └── camel_case.py       # Pydantic camelCase config
├── tests/
│   ├── unit/                   # Unit tests (pytest)
│   ├── integration/            # Integration tests
│   └── conftest.py             # Pytest fixtures
├── pyproject.toml              # Python dependencies (uv/pip)
├── pytest.ini                  # Pytest configuration
└── .env.example                # Environment variable template

frontend/
├── src/
│   ├── main.tsx                # React app entry point
│   ├── App.tsx                 # Root component
│   ├── pages/                  # Refine pages
│   │   ├── DatabaseList.tsx    # Database connection management
│   │   └── QueryTool.tsx       # Main query interface
│   ├── components/             # Reusable UI components
│   │   ├── SchemaTree.tsx      # Left sidebar tree view
│   │   ├── ColumnDetails.tsx   # Column information display
│   │   ├── SqlEditor.tsx       # Monaco editor wrapper
│   │   ├── QueryResults.tsx    # Table result display
│   │   └── NlQueryInput.tsx    # Natural language input
│   ├── services/               # API client
│   │   └── api.ts              # Axios/fetch backend calls
│   ├── types/                  # TypeScript types
│   │   ├── database.ts         # Database & metadata types
│   │   └── query.ts            # Query request/response types
│   └── styles/                 # Tailwind custom styles
│       └── index.css
├── tests/
│   └── unit/                   # Vitest tests
├── package.json                # Node dependencies
├── tsconfig.json               # TypeScript config (strict mode)
├── vite.config.ts              # Vite bundler config
└── tailwind.config.js          # Tailwind CSS config

db-query/                       # SQLite storage directory
└── db_query.db                 # Metadata cache database (created at runtime)
```

**Structure Decision**: Web application architecture selected (Option 2 from template). Separate `backend/` (FastAPI Python) and `frontend/` (React TypeScript) directories. Backend follows layered architecture: API routes → Services → Models. Frontend uses Refine framework structure with pages, components, and services. SQLite database stored in dedicated `db-query/` directory at repository root.

## Complexity Tracking

> **No violations - this section remains empty**

All constitution principles satisfied; no complexity justifications required.

---

## Post-Design Constitution Re-Check

**Date**: 2025-12-16  
**Phase**: After Phase 1 design completion

### Principle I: Strict Type Safety ✅
- Data models fully defined with Pydantic (backend) and TypeScript interfaces (frontend)
- OpenAPI contract validates all type definitions match between systems
- All API boundaries have explicit schemas

**Status**: PASS - Type safety maintained through design

### Principle II: Ergonomic Code Style ✅
- Project structure follows language conventions (FastAPI routes, React components)
- Clear separation of concerns (models, services, API routes)
- Documented best practices in research.md

**Status**: PASS - Ergonomic patterns documented

### Principle III: Data Model Standards ✅
- All Pydantic models use `alias_generator` for camelCase
- Validation rules embedded in models (URL format, SQL type checking)
- data-model.md documents all entities with validation rules

**Status**: PASS - Pydantic standards upheld in design

### Principle IV: API Conventions ✅
- OpenAPI contract defines REST endpoints with proper HTTP verbs
- Error responses structured (message, code, details)
- Status codes documented (200, 201, 400, 404, 500)

**Status**: PASS - REST conventions maintained

### Principle V: Open Access ✅
- No authentication endpoints in API contract
- CORS configured to allow all origins (documented in quickstart)
- Security warnings included in documentation

**Status**: PASS - Open access design confirmed

### Overall Re-Check Result: ✅ PASS

All constitution principles remain satisfied after Phase 1 design. API contracts, data models, and quickstart guide align with established governance. Ready to proceed to Phase 2 (tasks generation via `/speckit.tasks`).

