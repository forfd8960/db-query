# GitHub Copilot Instructions

## Project Overview

**DB Query Tool** - A web-based database query and export tool

**Primary Purpose**: 
- Connect to databases (PostgreSQL, MySQL) via connection URLs
- Execute SQL queries with natural language support
- Browse database metadata (tables, views, columns)
- Export query results in multiple formats (CSV, JSON, Excel)

**Key Technologies**:
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, OpenAI SDK
- **Frontend**: React 18+, TypeScript (strict mode), Ant Design, Tailwind CSS
- **Additional Libraries**: openpyxl (Excel generation), sqlparse (SQL validation), Monaco Editor (SQL editing)

**High-Level Architecture**:
- RESTful API backend with FastAPI
- React SPA frontend with type-safe TypeScript
- SQLite for metadata caching
- Stateless query execution and export generation

## Getting Started

**Prerequisites**:
- Python 3.11 or higher
- Node.js 18+ and npm/yarn
- Database access (PostgreSQL or MySQL)
- OpenAI API key (for natural language queries)

**Installation**:
```bash
# Backend
cd backend
pip install -r requirements.txt  # or use poetry/pipenv

# Frontend
cd frontend
npm install

# Environment
export OPENAI_API_KEY=your_key_here
```

**Running Locally**:
```bash
# Backend (from backend/ directory)
uvicorn src.main:app --reload --port 8000

# Frontend (from frontend/ directory)
npm run dev
```

## Development Workflow

**Build**:
- Backend: No build step (Python interpreted)
- Frontend: `npm run build` (creates optimized production bundle)

**Test**:
- Backend: `pytest` (unit and integration tests)
- Frontend: `npm test` (React Testing Library + Jest)
- API testing: Use `test.rest` file or Postman

**Debug**:
- Backend: Use VS Code debugger with FastAPI launch config
- Frontend: Browser DevTools + React DevTools extension
- API: Check FastAPI auto-docs at `http://localhost:8000/docs`

## Code Conventions

**Backend (Python)**:
- **Style**: Ergonomic Python (Pythonic idioms, clear naming)
- **Type Safety**: Mandatory type hints on all functions and methods
- **Models**: Use Pydantic for all request/response models
- **Naming**: camelCase for all API responses (via `CamelCaseModel` base class)
- **Validation**: Business logic in Pydantic models, not scattered in handlers

**Frontend (TypeScript)**:
- **Style**: Modern React patterns (hooks, functional components)
- **Type Safety**: TypeScript strict mode, no implicit `any`
- **Components**: Functional components with proper TypeScript interfaces
- **State**: React hooks for local state, context for global state
- **API**: Centralized API calls in `services/api.ts`

**File Organization**:
```
backend/src/
├── models/          # Pydantic models (request/response)
├── services/        # Business logic and external integrations
├── api/v1/          # FastAPI route handlers
└── utils/           # Shared utilities

frontend/src/
├── components/      # Reusable UI components
├── pages/           # Page-level components
├── services/        # API clients and external services
├── types/           # TypeScript type definitions
└── styles/          # Global styles
```

## Architecture Notes

**Component Boundaries**:
- **API Layer** (`backend/src/api/`): Route handlers, request validation, response formatting
- **Service Layer** (`backend/src/services/`): Business logic, database operations, external API calls
- **Model Layer** (`backend/src/models/`): Data structures, validation rules
- **UI Layer** (`frontend/src/components/`): Presentational components
- **State Management**: Local component state + props (no global state library needed yet)

**Data Flow Patterns**:
1. **Query Execution**: User → Frontend → API → QueryExecutor → Database → API → Frontend → Display
2. **Export**: QueryResults (frontend state) → API → Exporter Service → StreamingResponse → Browser Download
3. **Metadata**: Database → MetadataExtractor → SQLite Cache → API → Frontend Tree View

**Integration Points**:
- **OpenAI API**: Natural language to SQL conversion (`services/nl_converter.py`)
- **Database Connections**: Dynamic connection pooling via SQLAlchemy
- **Metadata Caching**: SQLite storage for table/column metadata

**Key Design Decisions**:
- **No Authentication**: Open access (suitable for internal/dev tools only)
- **Stateless Exports**: Files generated on-demand, streamed to client (no server storage)
- **SQL Safety**: All queries parsed and validated; only SELECT statements allowed
- **Auto-Limit**: Queries without LIMIT clause get automatic `LIMIT 1000`
- **Export Limits**: Maximum 100,000 rows per export to prevent resource exhaustion

## Common Tasks

### Adding a New API Endpoint

1. **Define Pydantic models** in `backend/src/models/`:
```python
class MyRequest(CamelCaseModel):
    field: str = Field(..., description="Description")

class MyResponse(CamelCaseModel):
    result: str
```

2. **Create route handler** in `backend/src/api/v1/`:
```python
@router.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest) -> MyResponse:
    # Business logic here or call service
    return MyResponse(result="success")
```

3. **Add TypeScript types** in `frontend/src/types/`:
```typescript
export interface MyRequest {
  field: string;
}

export interface MyResponse {
  result: string;
}
```

4. **Add API call** in `frontend/src/services/api.ts`:
```typescript
export async function myEndpoint(request: MyRequest): Promise<MyResponse> {
  const response = await fetch('/api/v1/my-endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return response.json();
}
```

### Adding a New Export Format

**Current Formats**: CSV, JSON, Excel

To add a new format (e.g., XML):

1. **Add enum value** in `backend/src/models/export.py`:
```python
class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    XML = "xml"  # NEW
```

2. **Create exporter** in `backend/src/services/export/xml_exporter.py`:
```python
class XMLExporter(BaseExporter):
    def export(self, columns: list[str], rows: list[dict]) -> bytes:
        # XML generation logic
        pass
```

3. **Register in export service** in `backend/src/services/export_service.py`:
```python
EXPORTERS = {
    ExportFormat.CSV: CSVExporter(),
    ExportFormat.JSON: JSONExporter(),
    ExportFormat.EXCEL: ExcelExporter(),
    ExportFormat.XML: XMLExporter(),  # NEW
}
```

4. **Add to frontend dropdown** in `frontend/src/components/ExportButton.tsx`:
```typescript
const menuItems = [
  { key: 'csv', label: 'Export as CSV' },
  { key: 'json', label: 'Export as JSON' },
  { key: 'excel', label: 'Export as Excel' },
  { key: 'xml', label: 'Export as XML' },  // NEW
];
```

### Common Debugging Scenarios

**Query Not Executing**:
- Check SQL syntax in Monaco editor
- Verify database connection URL is correct
- Check backend logs for sqlparse validation errors
- Ensure query is SELECT-only (other statements rejected)

**Export Download Not Starting**:
- Check browser console for errors
- Verify Content-Disposition header in response
- Check browser download settings (popup blockers)
- Verify row count is under 100,000 limit

**Type Errors in Frontend**:
- Check API response matches TypeScript interface
- Verify camelCase conversion in backend (`CamelCaseModel`)
- Use browser DevTools Network tab to inspect response

**Metadata Not Showing**:
- Check database connection is active
- Verify metadata extraction completed (check SQLite cache)
- Check backend logs for metadata extractor errors

---

## Technology Stack Reference

### Backend Stack
- **openpyxl**: Excel (XLSX) file generation - used in export feature

### Frontend Stack  
- **Ant Design**: UI component library for buttons, tables, dropdowns
- **Monaco Editor**: SQL code editor with syntax highlighting

### Current Features
1. **Database Management**: Add/update/list database connections
2. **Query Execution**: Execute SQL with validation and auto-LIMIT
3. **Natural Language Queries**: Convert English to SQL via OpenAI
4. **Metadata Browsing**: Tree view of tables/views/columns
5. **Query Results Export**: Download results in CSV/JSON/Excel formats (NEW in 003-data-export)

---

**Note**: This file is automatically updated when new features are planned. Manual additions should go between clearly marked sections to avoid conflicts.
