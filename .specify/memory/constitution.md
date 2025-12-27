<!--
Sync Impact Report:
Version change: Initial → 1.0.0
Added principles:
  - I. Strict Type Safety
  - II. Ergonomic Code Style
  - III. Data Model Standards
  - IV. API Conventions
  - V. Open Access
Added sections:
  - Technology Stack
  - Development Standards
Modified templates:
  - ✅ plan-template.md (reviewed for alignment)
  - ✅ spec-template.md (reviewed for alignment)
  - ✅ tasks-template.md (reviewed for alignment)
Follow-up TODOs: None
-->

# DB Query Tool Constitution

## Core Principles

### I. Strict Type Safety

**MUST** use strict type annotations in all code:
- Backend (Python): All functions, methods, and variables MUST have type hints
- Frontend (TypeScript): Strict mode MUST be enabled; all components, functions, and variables MUST be typed
- No implicit `any` types permitted without explicit justification

**Rationale**: Type safety prevents runtime errors, improves IDE support, and serves as living documentation. In a database query tool handling diverse data structures, strict typing is essential for correctness.

### II. Ergonomic Code Style

**MUST** follow language-specific ergonomic practices:
- Backend: Ergonomic Python style (readable, Pythonic idioms, clear naming)
- Frontend: Modern TypeScript/React patterns (hooks, functional components, composition)
- Code MUST be self-documenting through clear naming and structure
- Comments required only for non-obvious business logic or complex algorithms

**Rationale**: Readable code reduces cognitive load and maintenance burden. This project crosses language boundaries; each side must exemplify its language's best practices.

### III. Data Model Standards

**MUST** use Pydantic for all backend data models:
- All request/response schemas defined as Pydantic models
- Validation rules embedded in models, not scattered across handlers
- All backend-generated data MUST use camelCase naming (for frontend consistency)

**Rationale**: Pydantic provides runtime validation, automatic serialization, and OpenAPI schema generation. CamelCase consistency eliminates frontend mapping boilerplate.

### IV. API Conventions

**MUST** follow REST/JSON API standards:
- All responses in JSON format with camelCase keys
- HTTP status codes used correctly (200, 400, 404, 500, etc.)
- Error responses MUST include structured error details (message, code, field-level errors where applicable)

**Rationale**: Consistent API contracts simplify frontend integration and enable generic error handling.

### V. Open Access

**MUST NOT** implement authentication or authorization:
- All endpoints publicly accessible
- No user accounts, sessions, or access controls
- Suitable for development/internal tools only

**Rationale**: Per project requirements, this is a tool for unrestricted use. This principle serves as a security boundary marker for future decisions.

## Technology Stack

**Backend**:
- Python 3.11+ with FastAPI
- Pydantic for data validation and serialization
- SQLGlot for SQL parsing and transformation
- sqlparse for SQL validation
- OpenAI SDK for natural language to SQL conversion
- SQLite for metadata storage

**Frontend**:
- React 18+ with TypeScript (strict mode)
- Refine 5 for data management framework
- Ant Design for UI components
- Tailwind CSS for styling
- Monaco Editor for SQL editing

**Database Support**:
- Primary target: PostgreSQL
- Metadata extraction via PostgreSQL system catalogs
- Query execution limited to SELECT statements only (enforced via sqlparse)

## Development Standards

**SQL Safety**:
- All user-input SQL MUST be parsed by sqlparse before execution
- Only SELECT statements permitted; other operations MUST be rejected
- Queries without LIMIT clause MUST automatically append `LIMIT 1000`
- Parse errors MUST return structured error messages with line/column information

**Data Persistence**:
- Database connection URLs stored in local SQLite
- Extracted metadata (tables, views, columns) cached in SQLite
- Metadata format: JSON structures generated via LLM transformation from PostgreSQL catalogs

**LLM Integration**:
- Natural language queries converted to SQL via OpenAI API
- Context includes: database schema, table/column metadata, sample queries
- Generated SQL MUST pass through same validation pipeline as manual queries

## Governance

This constitution supersedes all other development practices. All code contributions MUST:
- Verify compliance with Core Principles before review
- Document any principle violations with explicit justification
- Include type annotations, validations, and error handling per standards

**Amendment Process**:
- Amendments require documented rationale
- Version bumped according to semantic versioning (MAJOR for breaking governance changes, MINOR for additions, PATCH for clarifications)
- Migration plan required for changes affecting existing code

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
