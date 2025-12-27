# Data Export Feature - Design Flow

**Feature Branch**: `003-data-export` | **Status**: Implemented | **Date**: 2025-12-27

## Purpose

Enable users to download SQL query results in three formats: CSV, JSON, and Excel (XLSX). The feature provides on-demand file generation with proper encoding, type preservation, and browser-triggered downloads.

## User Flow

1. **Execute Query** → User runs SQL query and sees results in table
2. **Click Export** → Export button appears next to row count display
3. **Select Format** → Dropdown shows CSV, JSON, Excel options
4. **Download Begins** → File streams directly to browser with timestamped filename

## Architecture

### Backend Design (Python/FastAPI)

**Polymorphic Exporter Pattern**:
- `BaseExporter` abstract class defines `export(columns, rows) -> bytes` interface
- Three concrete implementations: `CSVExporter`, `JSONExporter`, `ExcelExporter`
- Each handles format-specific encoding, type conversion, and special character escaping

**API Endpoint**: `POST /api/v1/databases/{dbName}/export`
- Validates row count (100K limit)
- Instantiates appropriate exporter based on format
- Streams file with `Content-Disposition` header for browser download
- Returns proper MIME types: `text/csv`, `application/json`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

### Frontend Design (React/TypeScript)

**ExportButton Component**:
- Ant Design Dropdown with three format options
- Loading state during export generation
- Success/error notifications via Ant Design message
- Disabled when no query results available

**Export API Client**:
- Fetch POST with blob response type
- Extracts filename from `Content-Disposition` header
- Creates temporary anchor element for download trigger
- Automatic cleanup after download

## Data Model

### ExportFormat Enum
```typescript
type ExportFormat = 'csv' | 'json' | 'excel'
```

### ExportRequest
```python
class ExportRequest(CamelCaseModel):
    format: ExportFormat
    query_results: dict[str, Any]  # {columns, rows, rowCount}
```

### QueryResults (existing)
- `columns`: list[str] - Column names
- `rows`: list[dict[str, Any]] - Data rows
- `rowCount`: int - Total rows

## Format-Specific Features

**CSV**: UTF-8 with BOM for Excel compatibility, QUOTE_MINIMAL escaping, null → empty string

**JSON**: Pretty-printed (2-space indent), type preservation (numbers as numbers), ISO 8601 dates, Unicode support

**Excel**: Native XLSX via openpyxl, bold headers, type-based cell formatting (numbers, dates, booleans), empty cells for nulls

## Key Implementation Details

**Duplicate Columns**: `disambiguate_column_names()` adds `_1`, `_2` suffixes automatically

**Filename Pattern**: `{dbName}_{timestamp}.{ext}` (e.g., `mydb_2025-12-27_143022.csv`)

**Error Handling**: Row limit validation (422), invalid format (400), generation failures (500)

**Security**: Filename sanitization removes `/<>:"|?*\` characters, 200-char length limit

**Performance**: Streaming response (no server-side storage), in-memory generation, BytesIO buffers

## Testing Strategy

- Unit tests for each exporter with edge cases (null values, special characters, duplicates)
- Integration test for export endpoint with all three formats
- Frontend component test for ExportButton interactions
- Manual testing: empty results, large datasets (100K rows), Unicode characters

## Dependencies

**New**: openpyxl 3.1+ (Excel generation, MIT license, 50M+ downloads/month)

**Existing**: FastAPI, Pydantic, React, Ant Design, TypeScript

---

**Total Implementation**: 63 tasks completed across 7 phases (Setup, Foundational, CSV, UI, JSON, Excel, Polish)
