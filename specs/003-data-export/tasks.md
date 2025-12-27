# Tasks: Query Results Export

**Input**: Design documents from `/specs/003-data-export/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml, quickstart.md

**Feature Branch**: `003-data-export`
**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3, US4)
- File paths follow web app structure: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependencies

- [X] T001 Add openpyxl dependency to backend/pyproject.toml or backend/requirements.txt (openpyxl>=3.1.0)
- [X] T002 [P] Install openpyxl in backend environment: pip install openpyxl
- [X] T003 [P] Create backend/src/services/export/ directory for export service modules
- [X] T004 [P] Create backend/src/models/export.py for export-related Pydantic models
- [X] T005 [P] Create backend/src/utils/filename.py for filename sanitization utilities
- [X] T006 [P] Create frontend/src/types/export.ts for export-related TypeScript types

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core export infrastructure shared across all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create ExportFormat enum (CSV, JSON, EXCEL) in backend/src/models/export.py
- [X] T008 Create ExportRequest Pydantic model in backend/src/models/export.py with format and queryResults fields
- [X] T009 Create BaseExporter abstract class in backend/src/services/export/base.py with export() method signature
- [X] T010 [P] Create sanitize_filename() function in backend/src/utils/filename.py (remove unsafe chars, limit length)
- [X] T011 [P] Create generate_filename() function in backend/src/utils/filename.py (pattern: {db_name}_{timestamp}.{ext})
- [X] T012 [P] Create disambiguate_column_names() utility in backend/src/utils/filename.py (handle duplicate columns)
- [X] T013 Create export API router in backend/src/api/v1/exports.py with FastAPI router setup
- [X] T014 Create POST /databases/{db_name}/export endpoint skeleton in backend/src/api/v1/exports.py
- [X] T015 Register exports router in backend/src/main.py with app.include_router()
- [X] T016 [P] Create ExportFormat TypeScript type in frontend/src/types/export.ts
- [X] T017 [P] Create ExportRequest TypeScript interface in frontend/src/types/export.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Export Query Results as CSV (Priority: P1) 🎯 MVP

**Goal**: Users can export query results as CSV files with proper UTF-8 encoding and special character escaping

**Independent Test**: Execute SQL query → Click Export → Select CSV → Download CSV file → Open in Excel/Google Sheets → Verify all data present with correct encoding

### Implementation for User Story 1

- [X] T018 [P] [US1] Create CSVExporter class in backend/src/services/export/csv_exporter.py inheriting from BaseExporter
- [X] T019 [US1] Implement export() method in CSVExporter using Python csv module with UTF-8 encoding and QUOTE_MINIMAL
- [X] T020 [US1] Add CSV format handler to export endpoint in backend/src/api/v1/exports.py
- [X] T021 [US1] Configure StreamingResponse for CSV with media_type="text/csv; charset=utf-8" in backend/src/api/v1/exports.py
- [X] T022 [US1] Add Content-Disposition header with sanitized filename in backend/src/api/v1/exports.py
- [X] T023 [US1] Add row count validation (max 100,000) in backend/src/api/v1/exports.py with EXPORT_TOO_LARGE error
- [X] T024 [US1] Handle special characters (commas, quotes, newlines) in CSVExporter with proper escaping
- [X] T025 [US1] Handle null values in CSVExporter (export as empty string, not "None")
- [X] T026 [US1] Handle empty result sets in CSVExporter (export headers only)

**Checkpoint**: CSV export fully functional - users can download query results as CSV files

---

## Phase 4: User Story 4 - Format Selection and Export Initiation (Priority: P1) 🎯 MVP

**Goal**: Users have an intuitive UI to select export format and initiate download

**Independent Test**: Display query results → See enabled Export button → Click button → See dropdown with format options → Select format → Download begins

### Implementation for User Story 4

- [X] T027 [P] [US4] Create ExportButton component in frontend/src/components/ExportButton.tsx with TypeScript interfaces
- [X] T028 [US4] Add Ant Design Dropdown with menu items for CSV, JSON, Excel in ExportButton.tsx
- [X] T029 [US4] Implement handleExport function in ExportButton.tsx with format parameter
- [X] T030 [US4] Add loading state management in ExportButton.tsx using useState hook
- [X] T031 [US4] Add disabled prop handling in ExportButton.tsx (disabled when no query results)
- [X] T032 [US4] Create exportQueryResults() function in frontend/src/services/api.ts
- [X] T033 [US4] Implement fetch POST request to /api/v1/databases/{dbName}/export in api.ts
- [X] T034 [US4] Handle blob response and trigger browser download in api.ts (create anchor element, click, cleanup)
- [X] T035 [US4] Extract filename from Content-Disposition header in api.ts
- [X] T036 [US4] Add error handling in api.ts with proper error message extraction from response
- [X] T037 [US4] Integrate ExportButton into QueryResults component in frontend/src/components/QueryResults.tsx
- [X] T038 [US4] Position ExportButton in QueryResults.tsx header area next to row count display
- [X] T039 [US4] Pass queryResults, dbName, and loading props to ExportButton in QueryResults.tsx
- [X] T040 [US4] Add success message notification in ExportButton.tsx using Ant Design message.success()
- [X] T041 [US4] Add error message notification in ExportButton.tsx using Ant Design message.error()

**Checkpoint**: Export UI fully functional - users can select CSV format and download files

---

## Phase 5: User Story 2 - Export Query Results as JSON (Priority: P2)

**Goal**: Users can export query results as JSON files with proper type preservation

**Independent Test**: Execute SQL query → Click Export → Select JSON → Download JSON file → Parse in browser/editor → Verify array of objects with correct types

### Implementation for User Story 2

- [X] T042 [P] [US2] Create JSONExporter class in backend/src/services/export/json_exporter.py inheriting from BaseExporter
- [X] T043 [US2] Implement export() method in JSONExporter using json.dumps with ensure_ascii=False and indent=2
- [X] T044 [US2] Add JSON format handler to export endpoint in backend/src/api/v1/exports.py
- [X] T045 [US2] Configure StreamingResponse for JSON with media_type="application/json; charset=utf-8" in backend/src/api/v1/exports.py
- [X] T046 [US2] Handle type preservation in JSONExporter: numbers as JSON numbers (not strings)
- [X] T047 [US2] Handle null values in JSONExporter (export as JSON null, not string "null")
- [X] T048 [US2] Handle datetime/date values in JSONExporter (convert to ISO 8601 strings via isoformat())
- [X] T049 [US2] Add default=str fallback for non-serializable objects in JSONExporter
- [X] T050 [US2] Update ExportButton menu in frontend/src/components/ExportButton.tsx to enable JSON option

**Checkpoint**: JSON export fully functional - users can download query results as JSON files with proper typing

---

## Phase 6: User Story 3 - Export Query Results as Excel (Priority: P3)

**Goal**: Users can export query results as Excel XLSX files with native type formatting

**Independent Test**: Execute SQL query → Click Export → Select Excel → Download XLSX file → Open in Excel/LibreOffice → Verify numbers are numbers, dates are dates

### Implementation for User Story 3

- [X] T051 [P] [US3] Create ExcelExporter class in backend/src/services/export/excel_exporter.py inheriting from BaseExporter
- [X] T052 [US3] Import openpyxl and create Workbook in ExcelExporter.export() method
- [X] T053 [US3] Create worksheet named "Query Results" in ExcelExporter
- [X] T054 [US3] Write column headers in row 1 of Excel worksheet in ExcelExporter
- [X] T055 [US3] Write data rows starting from row 2 in ExcelExporter
- [X] T056 [US3] Implement type-based cell formatting in ExcelExporter: int/float → number format
- [X] T057 [US3] Implement date/datetime formatting in ExcelExporter with Excel date serial numbers and custom number_format
- [X] T058 [US3] Handle null values in ExcelExporter (set cell.value = None for empty cells)
- [X] T059 [US3] Handle boolean values in ExcelExporter (export as Excel TRUE/FALSE)
- [X] T060 [US3] Save workbook to BytesIO buffer and return in ExcelExporter
- [X] T061 [US3] Add Excel format handler to export endpoint in backend/src/api/v1/exports.py
- [X] T062 [US3] Configure StreamingResponse for Excel with media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
- [X] T063 [US3] Update ExportButton menu in frontend/src/components/ExportButton.tsx to enable Excel option

**Checkpoint**: All user stories complete - users can export in all three formats

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and user experience enhancements

- [X] T064 Add INVALID_FORMAT error handling in backend/src/api/v1/exports.py (400 status with error code)
- [X] T065 Add EXPORT_GENERATION_FAILED error handling in backend/src/api/v1/exports.py (500 status with error code)
- [X] T066 Apply disambiguate_column_names() to handle duplicate column names across all exporters
- [X] T067 Add UTF-8 BOM to CSV export for better Excel compatibility in CSVExporter
- [X] T068 [P] Add input validation for ExportRequest in backend/src/models/export.py with Pydantic validators
- [X] T069 [P] Add comprehensive error messages in backend/src/api/v1/exports.py for all error scenarios
- [X] T070 [P] Add logging for export operations in backend/src/api/v1/exports.py (format, row count, success/failure)
- [ ] T071 Test empty result set exports across all three formats
- [ ] T072 Test exports with special characters (Chinese, emoji, quotes, commas) across all formats
- [ ] T073 Test large exports near 100,000 row limit
- [ ] T074 Test export with duplicate column names (verify _1, _2 suffixes)
- [ ] T075 [P] Update backend API documentation at /docs with export endpoint details
- [ ] T076 [P] Add unit tests for CSVExporter in backend/tests/unit/test_exporters.py
- [ ] T077 [P] Add unit tests for JSONExporter in backend/tests/unit/test_exporters.py
- [ ] T078 [P] Add unit tests for ExcelExporter in backend/tests/unit/test_exporters.py
- [ ] T079 [P] Add unit tests for filename utilities in backend/tests/unit/test_filename.py
- [ ] T080 [P] Add integration test for export API endpoint in backend/tests/integration/test_export_api.py
- [ ] T081 [P] Add React component tests for ExportButton in frontend/tests/ExportButton.test.tsx

**Checkpoint**: Feature complete with comprehensive error handling and test coverage

---

## Dependencies & Execution Order

### Critical Path (Must Complete in Order)
1. **Setup** (T001-T006) → **Foundational** (T007-T017) → User Stories can begin
2. **User Story 1** (T018-T026) + **User Story 4** (T027-T041) → **MVP Ready**
3. **User Story 2** (T042-T050) → **JSON Support Added**
4. **User Story 3** (T051-T063) → **All Formats Available**
5. **Polish** (T064-T081) → **Production Ready**

### Parallel Execution Opportunities

**After Foundational Phase Complete**:
- Backend CSV implementation (T018-T026) || Frontend UI implementation (T027-T041)
- JSON exporter (T042-T049) || Frontend JSON enable (T050)
- Excel exporter (T051-T062) || Frontend Excel enable (T063)
- Test writing (T076-T081) can start early and run in parallel with implementation

**Within Each User Story**:
- Backend exporter creation [P] || Frontend type definitions [P]
- Unit tests [P] can be written in parallel with implementation
- Documentation updates [P] can happen anytime

### Independent Story Completion

Each user story delivers standalone value:
- **After US1 + US4**: CSV export works end-to-end (MVP)
- **After US2**: JSON export adds API integration capability
- **After US3**: Excel export completes full feature set

---

## Implementation Strategy

### MVP First (Recommended)
Focus on User Stories 1 + 4 to deliver working CSV export quickly:
1. Complete T001-T017 (Setup + Foundation)
2. Complete T018-T026 (CSV backend)
3. Complete T027-T041 (Export UI)
4. Test end-to-end CSV export
5. **Ship MVP** ✅

### Incremental Delivery
After MVP, add formats incrementally:
1. Add JSON (T042-T050) - 2-3 hours
2. Test JSON export
3. **Ship JSON support** ✅
4. Add Excel (T051-T063) - 3-4 hours
5. Test Excel export
6. **Ship complete feature** ✅
7. Polish (T064-T081) - ongoing

### Parallel Development
If multiple developers available:
- **Developer A**: Backend exporters (T018-T026, T042-T049, T051-T062)
- **Developer B**: Frontend UI (T027-T041, T050, T063)
- **Developer C**: Tests and polish (T076-T081, T064-T075)

---

## Validation Checklist

Before marking feature complete, verify:

### User Story 1 (CSV Export)
- [ ] CSV file downloads with correct filename pattern
- [ ] CSV opens in Excel/Google Sheets without encoding issues
- [ ] Special characters (commas, quotes, newlines) properly escaped
- [ ] Chinese/emoji characters display correctly (UTF-8)
- [ ] Null values appear as empty cells (not "None")
- [ ] Empty result sets export with headers only

### User Story 2 (JSON Export)
- [ ] JSON file downloads with .json extension
- [ ] JSON parses correctly (valid syntax)
- [ ] Numbers are JSON numbers (not quoted strings)
- [ ] Null values are JSON null (not string "null")
- [ ] Dates formatted as ISO 8601 strings
- [ ] Array of objects structure matches spec

### User Story 3 (Excel Export)
- [ ] XLSX file downloads and opens in Excel
- [ ] Numbers are formatted as numbers (can sum/calculate)
- [ ] Dates are formatted as Excel dates (can calculate)
- [ ] Null values appear as empty cells
- [ ] Column headers in row 1, bold formatting works
- [ ] All columns visible without horizontal scrolling issues

### User Story 4 (Export UI)
- [ ] Export button hidden/disabled when no query results
- [ ] Export button visible/enabled when results displayed
- [ ] Dropdown shows all three format options
- [ ] Loading indicator appears during export
- [ ] Success message shown on completion
- [ ] Error message shown on failure

### Cross-Cutting
- [ ] Exports >100,000 rows rejected with clear error
- [ ] Duplicate column names disambiguated correctly
- [ ] Filenames sanitized (no unsafe characters)
- [ ] All exports complete within 5 seconds for 10K rows
- [ ] Browser download triggers automatically
- [ ] Content-Disposition header includes correct filename

---

## Performance Targets

- **CSV**: <500ms for 10,000 rows
- **JSON**: <800ms for 10,000 rows  
- **Excel**: <2s for 10,000 rows
- **All formats**: <5s for 100,000 rows (max supported)

## Reference Documentation

- **Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Research Decisions**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **API Contract**: [contracts/api.yaml](contracts/api.yaml)
- **Quick Start Guide**: [quickstart.md](quickstart.md)
