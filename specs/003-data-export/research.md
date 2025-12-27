# Research: Query Results Export

**Feature**: Query Results Export  
**Phase**: Phase 0 - Research & Technology Decisions  
**Date**: 2025-12-27

## Research Questions & Resolutions

### 1. Python Library for Excel Generation

**Question**: Which Python library should we use for XLSX file generation?

**Options Evaluated**:
- **openpyxl**: Pure Python, supports XLSX format, actively maintained, 50M+ downloads/month
- **xlsxwriter**: Pure Python, write-only, good performance, 10M+ downloads/month
- **pandas**: Heavyweight, requires openpyxl or xlsxwriter as engine, overkill for simple export

**Decision**: **openpyxl**

**Rationale**:
- Most popular and actively maintained XLSX library in Python ecosystem
- Direct XLSX support without requiring intermediate dependencies
- Provides full control over cell formatting and data types (numbers, dates)
- MIT license, compatible with project requirements
- Simple API for basic use cases: `workbook.create_sheet()`, `cell.value = data`
- Can set number formats explicitly: `cell.number_format = 'General'` for numbers, `'yyyy-mm-dd'` for dates

**Alternatives Considered**:
- xlsxwriter: Rejected because write-only limitation prevents potential future features (e.g., template-based exports)
- pandas: Rejected due to heavyweight dependency for simple export needs; would add 30+ MB to deployment

### 2. CSV Generation Approach

**Question**: Should we use Python's `csv` module or a third-party library?

**Decision**: **Python standard library `csv` module**

**Rationale**:
- Built-in, no additional dependencies
- Handles escaping and quoting automatically via `csv.QUOTE_MINIMAL`
- Supports UTF-8 encoding via `open(file, 'w', encoding='utf-8', newline='')`
- Proven, stable API since Python 2.x
- Adequate performance for target scale (100,000 rows)

**Implementation Pattern**:
```python
import csv
import io

def export_csv(columns: list[str], rows: list[dict]) -> io.StringIO:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(rows)
    return output
```

**Alternatives Considered**: None needed - standard library is optimal choice

### 3. JSON Export Format

**Question**: What JSON structure should we use for row data?

**Options Evaluated**:
- **Array of objects** (e.g., `[{col1: val1, col2: val2}, ...]`): Most common, self-documenting
- **Columnar format** (e.g., `{columns: [...], data: [[...], [...]]}`): More compact but less readable
- **Array of arrays** (e.g., `[[val1, val2], ...]` with separate columns array): Compact but loses key-value mapping

**Decision**: **Array of objects**

**Rationale**:
- Most intuitive format for developers and API consumers
- Self-documenting: column names embedded with each row
- Easy to consume in JavaScript/Python without additional mapping
- Matches common API response patterns (REST conventions)
- Type preservation via native JSON types (number, string, null, boolean)

**Implementation**:
```python
import json

def export_json(rows: list[dict]) -> str:
    return json.dumps(rows, ensure_ascii=False, indent=2, default=str)
```

**Type Handling**:
- Numbers: Export as JSON numbers (not strings)
- Null: Export as JSON `null`
- Dates: Convert to ISO 8601 strings (`datetime.isoformat()`)
- Boolean: Export as JSON boolean
- Other objects: Convert to string via `default=str`

**Alternatives Considered**:
- Columnar format: Rejected due to poor readability and additional parsing complexity
- Array of arrays: Rejected due to loss of key-value semantics

### 4. File Download Mechanism

**Question**: Should we store files on server or stream directly to client?

**Decision**: **Stream directly to client (StreamingResponse)**

**Rationale**:
- No server-side file storage needed (reduces complexity and disk usage)
- FastAPI's `StreamingResponse` perfect for this use case
- Memory efficient: can generate and stream incrementally for large datasets
- No cleanup required (no temp files to delete)
- Faster response (no disk I/O overhead)

**Implementation Pattern**:
```python
from fastapi.responses import StreamingResponse
import io

@router.get("/databases/{db_name}/export/{format}")
async def export_query_results(db_name: str, format: str):
    # Generate export content
    content = generate_export(format, query_results)
    
    # Determine MIME type
    mime_types = {
        'csv': 'text/csv',
        'json': 'application/json',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    # Generate filename
    filename = f"{db_name}_{timestamp}.{format}"
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type=mime_types[format],
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

**Alternatives Considered**:
- Server-side file storage: Rejected due to added complexity (file cleanup, disk space management, potential race conditions)
- Pre-signed URLs (S3-style): Overkill for this use case; adds external dependency

### 5. Filename Generation Strategy

**Question**: What format should exported filenames follow?

**Decision**: **`{database_name}_{timestamp}.{extension}`**

**Examples**:
- `mydb_2025-12-27_143022.csv`
- `production_2025-12-27_143022.json`
- `analytics_2025-12-27_143022.xlsx`

**Rationale**:
- Database name provides context (which database was queried)
- Timestamp ensures uniqueness and indicates when export was created
- Timestamp format `YYYY-MM-DD_HHMMSS` is sortable and human-readable
- Extension indicates format

**Sanitization Rules**:
- Remove or replace special characters: `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`
- Replace spaces with underscores
- Limit length to 200 characters (reasonable for most filesystems)
- Convert to ASCII-safe characters (remove accents, etc.)

**Implementation**:
```python
import re
from datetime import datetime

def sanitize_filename(name: str) -> str:
    # Remove unsafe characters
    name = re.sub(r'[/<>:"|?*\\]', '_', name)
    # Replace spaces
    name = name.replace(' ', '_')
    # Limit length
    return name[:200]

def generate_filename(db_name: str, format: str) -> str:
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    safe_db_name = sanitize_filename(db_name)
    return f"{safe_db_name}_{timestamp}.{format}"
```

**Alternatives Considered**:
- UUID-based names: Rejected due to poor human readability
- Query hash in filename: Rejected as unnecessarily complex and not user-friendly

### 6. Excel Data Type Formatting

**Question**: How should we handle data types in Excel exports?

**Decision**: **Explicit cell formatting based on Python data types**

**Type Mapping**:
- Python `int`/`float` → Excel number (no quotes)
- Python `str` → Excel text
- Python `datetime`/`date` → Excel date (with date number format)
- Python `None` → Empty cell (not string "None")
- Python `bool` → Excel boolean (TRUE/FALSE)

**Implementation Pattern**:
```python
from openpyxl import Workbook
from datetime import datetime, date

def set_cell_value(cell, value):
    cell.value = value
    
    if isinstance(value, (int, float)):
        cell.number_format = 'General'  # Number format
    elif isinstance(value, datetime):
        cell.number_format = 'yyyy-mm-dd hh:mm:ss'
    elif isinstance(value, date):
        cell.number_format = 'yyyy-mm-dd'
    # Strings and booleans use default formatting
```

**Rationale**:
- Preserves data types so Excel can perform calculations on numbers
- Dates are actual Excel dates (not text strings), enabling date calculations
- Null values shown as empty cells (Excel convention)
- Users can apply formulas directly without type conversion

**Alternatives Considered**:
- Everything as text: Rejected because it breaks Excel's calculation features
- Auto-detection: Rejected because Python already provides type information from database

### 7. Row Limit Handling

**Question**: How should we handle large result sets?

**Decision**: **100,000 row hard limit with clear error message**

**Rationale**:
- Prevents memory exhaustion and timeouts
- 100,000 rows ≈ 10-50MB file size (reasonable for download)
- Typical query results are much smaller (<10,000 rows)
- Error message guides users to add LIMIT clause to their query

**Implementation**:
```python
MAX_EXPORT_ROWS = 100_000

def validate_export_size(row_count: int):
    if row_count > MAX_EXPORT_ROWS:
        raise ValueError(
            f"Export limited to {MAX_EXPORT_ROWS:,} rows. "
            f"Your query returned {row_count:,} rows. "
            f"Please add a LIMIT clause to your query."
        )
```

**Error Response** (HTTP 400):
```json
{
  "error": {
    "code": "EXPORT_TOO_LARGE",
    "message": "Export limited to 100,000 rows. Your query returned 250,000 rows. Please add a LIMIT clause to your query."
  }
}
```

**Alternatives Considered**:
- Pagination: Rejected as overly complex; users can modify query
- Streaming without limit: Rejected due to memory/timeout risks
- Configurable limit: Deferred to future enhancement (YAGNI)

### 8. Duplicate Column Name Handling

**Question**: How should we handle queries with duplicate column names?

**Decision**: **Append numeric suffixes (_1, _2, etc.) to duplicates**

**Example**:
```
SELECT id, name, id FROM users
→ Columns: ["id", "name", "id_1"]
```

**Implementation**:
```python
def disambiguate_column_names(columns: list[str]) -> list[str]:
    seen = {}
    result = []
    
    for col in columns:
        if col in seen:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            result.append(col)
    
    return result
```

**Rationale**:
- Ensures all columns are exported (no data loss)
- Clear, predictable naming pattern
- Matches common database tool behavior (e.g., pgAdmin, DBeaver)
- Users can identify duplicates easily

**Alternatives Considered**:
- Use column position: Rejected due to poor clarity (e.g., `id_0`, `id_2`)
- Fail with error: Rejected as too strict; SQL allows duplicate names

## Technology Stack Summary

### Backend Dependencies (New)
- **openpyxl** ^3.1.0: Excel file generation
  - License: MIT
  - Size: ~3MB
  - Install: `pip install openpyxl`

### Backend Standard Library (No New Dependencies)
- **csv**: CSV generation
- **json**: JSON generation
- **io**: In-memory file handling
- **datetime**: Timestamp generation

### Frontend Dependencies (No New Dependencies)
- Ant Design: Already available for UI components (Button, Dropdown, Menu)
- Existing API service pattern for HTTP calls

## Performance Considerations

### Expected Performance
- CSV: ~1 second for 10,000 rows (~1MB file)
- JSON: ~1.5 seconds for 10,000 rows (~2MB file)
- Excel: ~2-3 seconds for 10,000 rows (~500KB file)

### Memory Usage
- Streaming approach: Peak memory ~2x file size
- 10,000 rows: <10MB peak memory
- 100,000 rows: <100MB peak memory (acceptable)

### Optimization Opportunities (Future)
- Chunked streaming for very large exports (>50,000 rows)
- Gzip compression for CSV/JSON (Content-Encoding: gzip)
- Background job processing for exports >50,000 rows

## Best Practices Applied

### Backend
1. **Single Responsibility**: Each exporter class handles one format
2. **Open/Closed**: Base exporter interface allows future format additions
3. **Type Safety**: Pydantic models with strict type hints
4. **Error Handling**: Specific exceptions for each failure mode
5. **Testing**: Unit tests for each exporter, integration tests for API

### Frontend
1. **Component Composition**: ExportButton as standalone, reusable component
2. **Type Safety**: TypeScript strict mode, all props typed
3. **User Feedback**: Loading states, success/error notifications
4. **Accessibility**: Keyboard navigation, ARIA labels
5. **Error Boundaries**: Graceful degradation if export fails

## Security Considerations

### File Download Safety
- Proper Content-Disposition header prevents browser misinterpretation
- MIME type validation prevents content-type confusion
- Filename sanitization prevents directory traversal

### Data Exposure
- No additional data exposed beyond what's already in query results
- Export uses same database connection and query execution as display
- No server-side file persistence (no residual data on disk)

### Rate Limiting (Future Consideration)
- Current implementation: No rate limiting (consistent with query execution)
- Future: Consider rate limiting if export abuse becomes issue

## Open Questions / Future Enhancements

None identified. All technical decisions resolved. Feature ready for Phase 1 (Design).
