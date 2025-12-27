# Implementation Plan: Query Results Export

**Branch**: `003-data-export` | **Date**: 2025-12-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-data-export/spec.md`

## Summary

Add export functionality to the database query tool, enabling users to download query results in three formats: CSV, JSON, and Excel (XLSX). The feature includes a backend API endpoint for export generation and a frontend UI component for format selection and download initiation. Export files are generated on-demand with proper encoding, type preservation, and meaningful filenames including database name and timestamp. The implementation prioritizes CSV support (P1), followed by JSON (P2) and Excel (P3), with comprehensive error handling and user feedback.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: 
- Backend: FastAPI, Pydantic, openpyxl (Excel generation)
- Frontend: React 18+, Ant Design, TypeScript (strict mode)

**Storage**: Query results are transient (not persisted); export files generated on-demand and streamed to client  
**Testing**: pytest (backend unit/integration), React Testing Library (frontend)  
**Target Platform**: Web application (backend: Linux/macOS server, frontend: modern browsers)  
**Project Type**: Web (backend API + frontend SPA)  
**Performance Goals**: Export completion within 5 seconds for 10,000 rows; handle up to 100,000 rows per export  
**Constraints**: File size reasonable (<50MB typical); UTF-8 encoding mandatory; proper MIME types for downloads  
**Scale/Scope**: Single feature extending existing query execution; ~3 new API endpoints, ~2 new React components, ~5 new Python modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. Strict Type Safety**
- All Python export functions will include complete type hints (Pydantic models, return types)
- TypeScript export UI components will use strict mode with full type annotations
- No implicit `any` types in format selection or download handling

✅ **II. Ergonomic Code Style**
- Python: Export formatters follow single responsibility principle, clear naming (e.g., `CSVExporter`, `JSONExporter`)
- TypeScript: React functional components with hooks, composition pattern for export button
- Self-documenting code with minimal comments

✅ **III. Data Model Standards**
- Export request/response models defined as Pydantic models
- All API responses use camelCase (consistent with existing codebase)
- Validation rules in models (format enum, row limit validation)

✅ **IV. API Conventions**
- Export endpoint returns file streams with proper HTTP headers (Content-Type, Content-Disposition)
- Error responses structured with message, code, field-level errors
- Proper HTTP status codes (200 for success, 400 for invalid format, 500 for generation errors)

✅ **V. Open Access**
- No authentication required for export functionality
- Consistent with existing query execution endpoints

### Additional Considerations

**SQL Safety**: Export feature reuses existing query result data (already validated by query executor). No new SQL parsing required.

**Data Persistence**: Export files are ephemeral (streamed directly to client); no server-side file storage.

**Dependencies**: New dependency `openpyxl` required for Excel generation (well-maintained, MIT license, 50M+ downloads/month).

### Gate Status: ✅ PASSED

All constitution principles are satisfied. No violations. Ready for Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── export.py              # NEW: ExportRequest, ExportFormat enum
│   ├── services/
│   │   ├── export/                # NEW: Export service module
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base exporter interface
│   │   │   ├── csv_exporter.py    # CSV export implementation
│   │   │   ├── json_exporter.py   # JSON export implementation
│   │   │   └── excel_exporter.py  # Excel export implementation
│   │   └── export_service.py      # NEW: Export orchestration
│   ├── api/
│   │   └── v1/
│   │       └── exports.py         # NEW: Export API endpoints
│   └── utils/
│       └── filename.py            # NEW: Filename sanitization
└── tests/
    ├── unit/
    │   └── test_exporters.py      # NEW: Unit tests for exporters
    └── integration/
        └── test_export_api.py     # NEW: Integration tests for export API

frontend/
├── src/
│   ├── components/
│   │   ├── ExportButton.tsx       # NEW: Export button with format selection
│   │   └── QueryResults.tsx       # MODIFIED: Add export button integration
│   ├── services/
│   │   └── api.ts                 # MODIFIED: Add export API calls
│   └── types/
│       └── export.ts              # NEW: Export-related TypeScript types
└── tests/
    └── ExportButton.test.tsx      # NEW: Component tests
```

**Structure Decision**: Web application structure with backend (Python/FastAPI) and frontend (TypeScript/React). Export functionality is organized as:
- Backend: New service module under `services/export/` following existing pattern (similar to `services/metadata_extractor.py`)
- Frontend: New component `ExportButton` integrated into existing `QueryResults` component
- Models follow existing patterns: Pydantic models in `backend/src/models/`, TypeScript types in `frontend/src/types/`

## Complexity Tracking

No violations detected. All constitution principles satisfied.

## Phase Completion Summary

### Phase 0: Research ✅ COMPLETE

**Output**: [research.md](research.md)

**Key Decisions**:
1. **CSV Generation**: Python stdlib `csv` module (no dependencies)
2. **JSON Format**: Array of objects with type preservation
3. **Excel Library**: openpyxl (most popular, MIT license)
4. **File Delivery**: StreamingResponse (no server storage)
5. **Filename Pattern**: `{db_name}_{timestamp}.{ext}`
6. **Row Limit**: 100,000 rows hard limit
7. **Type Handling**: Explicit type mapping for each format
8. **Duplicate Columns**: Numeric suffix disambiguation

**All NEEDS CLARIFICATION items resolved**: ✅

---

### Phase 1: Design ✅ COMPLETE

**Outputs**:
- [data-model.md](data-model.md): Entity definitions, validation rules, type mappings
- [contracts/api.yaml](contracts/api.yaml): OpenAPI 3.1 specification
- [quickstart.md](quickstart.md): Developer implementation guide

**Key Artifacts**:
1. **Data Models**: ExportFormat enum, ExportRequest, ExportMetadata, type mappings
2. **API Contract**: POST `/databases/{dbName}/export` with complete schemas
3. **Implementation Guide**: Phased approach (CSV→JSON→Excel), code samples

**Constitution Re-check**: ✅ PASSED

All design decisions align with constitution:
- Type safety maintained (Pydantic models, TypeScript strict mode)
- Ergonomic code patterns (single responsibility exporters, React hooks)
- Data models use Pydantic with camelCase serialization
- API follows REST conventions with proper status codes
- No authentication (open access principle)

---

### Phase 2: Planning Complete

**Next Command**: `/speckit.tasks` to generate implementation tasks from this plan

**Ready for Implementation**: ✅ YES

All prerequisites satisfied:
- Technical decisions documented
- Data models designed
- API contracts specified
- Implementation guide created
- Agent context updated
