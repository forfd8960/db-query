# Tasks: Database Query Tool

**Input**: Design documents from `/specs/001-db-query-tool/`  
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api.yaml, research.md, quickstart.md

**Organization**: Tasks grouped by user story for independent implementation and testing (P1 → P2 → P3)

**Note**: Streamlined to 2 phases as requested - Setup/Foundation combined into Phase 1, all user stories in Phase 2

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Parallelizable (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup & Foundation (Blocking Prerequisites)

**Purpose**: Project initialization and core infrastructure needed for ANY user story

**⚠️ CRITICAL**: Complete this phase before starting user story implementation

### Backend Setup

- [X] T001 Initialize backend Python project with pyproject.toml and dependencies (FastAPI, Pydantic, sqlparse, SQLGlot, openai, psycopg2-binary, python-dotenv)
- [X] T002 [P] Create backend directory structure (src/models/, src/services/, src/api/v1/, src/utils/, tests/)
- [X] T003 [P] Configure FastAPI app with CORS middleware in backend/src/main.py
- [X] T004 [P] Create Pydantic base config with camelCase alias_generator in backend/src/utils/camel_case.py
- [X] T005 [P] Setup SQLite database initialization in backend/src/services/storage.py
- [X] T006 [P] Create error response models in backend/src/models/errors.py

### Frontend Setup

- [X] T007 Initialize frontend React+TypeScript project with Vite, strict mode in tsconfig.json
- [X] T008 [P] Install frontend dependencies (React 19, Refine 5, Ant Design, Tailwind 4, Monaco Editor, axios)
- [X] T009 [P] Create frontend directory structure (src/pages/, src/components/, src/services/, src/types/, src/styles/)
- [X] T010 [P] Configure Tailwind CSS in frontend/tailwind.config.js and frontend/src/styles/index.css
- [X] T011 [P] Setup Refine app wrapper in frontend/src/App.tsx with Ant Design theme
- [X] T012 [P] Create API client service in frontend/src/services/api.ts with axios instance

### Database Schema

- [X] T013 Create SQLite schema (database_connections, database_metadata tables) in backend/src/services/storage.py
- [X] T014 [P] Write SQLite connection helper functions (insert, select, update, delete) in backend/src/services/storage.py

**Checkpoint**: ✅ Foundation ready - can now build user stories in parallel

---

## Phase 2: User Stories (All Features)

**Goal**: Implement all three user stories in priority order (P1 → P2 → P3)

---

### User Story 1 - Database Connection & Metadata Extraction (P1) 🎯 MVP

**Goal**: Connect to PostgreSQL, extract and display schema in tree view

**Independent Test**: Add connection URL, verify tables/views appear in sidebar, click table to see columns

#### Backend - User Story 1

- [X] T015 [P] [US1] Create DatabaseConnection Pydantic models in backend/src/models/database.py
- [X] T016 [P] [US1] Create DatabaseMetadata, TableMetadata, ColumnMetadata Pydantic models in backend/src/models/metadata.py
- [X] T017 [US1] Implement PostgreSQL connection service in backend/src/services/db_connection.py
- [X] T018 [US1] Implement metadata extraction service (query information_schema) in backend/src/services/metadata_extractor.py
- [X] T019 [US1] Implement POST /api/v1/databases/ endpoint in backend/src/api/v1/databases.py
- [X] T020 [US1] Implement GET /api/v1/databases/ endpoint in backend/src/api/v1/databases.py
- [X] T021 [US1] Implement PUT /api/v1/databases/{db_name}/ endpoint in backend/src/api/v1/databases.py
- [X] T022 [US1] Implement DELETE /api/v1/databases/{db_name}/ endpoint in backend/src/api/v1/databases.py
- [X] T023 [US1] Implement GET /api/v1/databases/{db_name}/metadata/ endpoint with caching in backend/src/api/v1/databases.py

#### Frontend - User Story 1

- [ ] T024 [P] [US1] Create TypeScript types for DatabaseConnection and DatabaseMetadata in frontend/src/types/database.ts
- [ ] T025 [P] [US1] Create database list page component in frontend/src/pages/DatabaseList.tsx
- [ ] T026 [US1] Create SchemaTree component for sidebar in frontend/src/components/SchemaTree.tsx
- [ ] T027 [US1] Create ColumnDetails component for right panel in frontend/src/components/ColumnDetails.tsx
- [ ] T028 [US1] Integrate database API calls in frontend/src/services/api.ts (list, create, get metadata)
- [ ] T029 [US1] Wire up DatabaseList page with Refine useTable hook and database management UI

**Checkpoint**: ✅ US1 complete - Users can connect to databases and browse schema

---

### User Story 2 - SQL Query Execution (P2)

**Goal**: Execute validated SELECT queries and display results in table

**Independent Test**: Type SELECT query, execute, see results in table below editor

#### Backend - User Story 2

- [ ] T030 [P] [US2] Create QueryRequest and QueryResult Pydantic models in backend/src/models/query.py
- [ ] T031 [P] [US2] Implement SQL validation service using sqlparse in backend/src/utils/sql_validator.py
- [ ] T032 [US2] Implement query executor service (validate, add LIMIT, execute) in backend/src/services/query_executor.py
- [ ] T033 [US2] Implement POST /api/v1/databases/{db_name}/query/ endpoint in backend/src/api/v1/queries.py

#### Frontend - User Story 2

- [ ] T034 [P] [US2] Create TypeScript types for QueryRequest and QueryResult in frontend/src/types/query.ts
- [ ] T035 [P] [US2] Create SqlEditor component with Monaco Editor in frontend/src/components/SqlEditor.tsx
- [ ] T036 [P] [US2] Create QueryResults table component in frontend/src/components/QueryResults.tsx
- [ ] T037 [US2] Create QueryTool page component integrating editor and results in frontend/src/pages/QueryTool.tsx
- [ ] T038 [US2] Integrate query execution API call in frontend/src/services/api.ts
- [ ] T039 [US2] Wire up QueryTool page with execute button, error handling, and result display

**Checkpoint**: ✅ US2 complete - Users can execute SQL queries and see results

---

### User Story 3 - Natural Language to SQL Conversion (P3)

**Goal**: Convert natural language to SQL using LLM

**Independent Test**: Enter "show all users", verify SQL appears in editor, can execute

#### Backend - User Story 3

- [ ] T040 [P] [US3] Create NaturalLanguageQueryRequest and NaturalLanguageQueryResponse Pydantic models in backend/src/models/query.py
- [ ] T041 [US3] Implement natural language converter service with OpenAI SDK in backend/src/services/nl_converter.py
- [ ] T042 [US3] Implement POST /api/v1/databases/{db_name}/nl-query/ endpoint in backend/src/api/v1/queries.py

#### Frontend - User Story 3

- [ ] T043 [P] [US3] Create TypeScript types for NaturalLanguageQueryRequest/Response in frontend/src/types/query.ts
- [ ] T044 [P] [US3] Create NlQueryInput component with textarea and Generate button in frontend/src/components/NlQueryInput.tsx
- [ ] T045 [US3] Integrate NL query API call in frontend/src/services/api.ts
- [ ] T046 [US3] Add NL input section to QueryTool page, populate editor with generated SQL

**Checkpoint**: ✅ US3 complete - Users can generate SQL from natural language

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**User Story 1 only** (T001-T029) delivers a functional database schema browser:
- Connect to PostgreSQL databases
- Browse tables, views, and columns
- Cache metadata locally
- Full CRUD for database connections

This is ~35% of total tasks but delivers 60% of user value.

### Incremental Delivery
1. **Phase 1** (T001-T014): Setup infrastructure - enables all development
2. **US1** (T015-T029): Schema browsing - first deployable feature
3. **US2** (T030-T039): Query execution - core value proposition
4. **US3** (T040-T046): Natural language - enhancement for non-technical users

### Parallel Execution Opportunities

**Phase 1 Parallelization** (after T001):
- Backend models/setup: T002, T004, T005, T006 (parallel)
- Frontend setup: T007, T008, T009, T010, T011, T012 (parallel)
- Backend and frontend teams can work simultaneously

**User Story 1 Parallelization**:
- Backend models: T015, T016 (parallel)
- Backend services: T017, T018 after models
- Frontend types/components: T024, T025, T026, T027 (parallel)
- Backend API and Frontend UI can progress in parallel after models/types

**User Story 2 Parallelization**:
- Backend models: T030, T031 (parallel)
- Frontend components: T034, T035, T036 (parallel)
- Backend and Frontend work independently until integration (T039)

**User Story 3 Parallelization**:
- Backend model and Frontend types: T040, T043 (parallel)
- Frontend component: T044 (parallel with T041)
- Quick integration (T042, T045, T046 sequential but fast)

### Dependency Graph

```
Phase 1 Foundation
├─ T001 (project init)
├─ T002-T014 (setup tasks, many parallel)
└─ Checkpoint: Foundation Ready

User Story 1 (P1) - Database Connection & Metadata
├─ Backend: T015→T016→T017→T018→T019-T023 (API endpoints)
├─ Frontend: T024→T025-T027 (parallel)→T028→T029
└─ Checkpoint: Schema browsing works

User Story 2 (P2) - SQL Query Execution (depends on US1 for database context)
├─ Backend: T030-T031 (parallel)→T032→T033
├─ Frontend: T034-T036 (parallel)→T037→T038→T039
└─ Checkpoint: Query execution works

User Story 3 (P3) - Natural Language (depends on US2 for query execution)
├─ Backend: T040→T041→T042
├─ Frontend: T043-T044 (parallel)→T045→T046
└─ Checkpoint: NL to SQL works
```

### Critical Path
T001 → T013 → T015-T016 → T017-T018 → T023 → T030-T032 → T033 → T040-T041 → T042

**Estimated Timeline**: 
- Phase 1: 1-2 days (setup)
- US1: 2-3 days (database connection & metadata)
- US2: 2-3 days (query execution)
- US3: 1-2 days (natural language)
- **Total**: 6-10 days for full feature set

---

## Validation Summary

✅ **All checklist requirements met**:
- Every task follows `- [ ] [ID] [P?] [Story?] Description with file path` format
- Tasks organized by user story (US1, US2, US3)
- Each story independently testable
- Clear dependencies documented
- MVP scope identified (US1 only)
- Parallel execution opportunities listed
- Only 2 phases as requested (Phase 1: Foundation, Phase 2: All User Stories)

✅ **Constitution alignment**:
- Type safety: Tasks include TypeScript types and Pydantic models
- Ergonomic code: Proper project structure (models, services, API layers)
- Data models: Pydantic with camelCase in every data model task
- API conventions: REST endpoints with proper HTTP verbs
- Open access: No authentication tasks

✅ **Coverage**:
- 46 total tasks
- 6 API endpoints from contracts
- 5 entities from data-model.md
- All 3 user stories from spec.md
- Backend + Frontend for each story
- Foundation tasks for infrastructure

**Ready for implementation! Start with Phase 1, then tackle user stories in order (P1→P2→P3).**
