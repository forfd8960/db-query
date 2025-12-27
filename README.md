# Database Query Tool

A full-stack web application for managing PostgreSQL and MySQL database connections, browsing schemas, and executing SQL queries with natural language support.

## Features

### 🔌 User Story 1: Database Connection Management
- **Create, update, and delete** PostgreSQL and MySQL database connections
- **Browse database schemas** with interactive tree view
- **View table metadata** including columns, types, primary keys, and row counts
- **Multi-database support** - manage both PostgreSQL and MySQL connections simultaneously
- **Test connections** before saving
- **SQLite-based storage** for connection metadata with automatic caching

### 💻 User Story 2: SQL Query Execution
- **Monaco Editor** with SQL syntax highlighting
- **Execute SELECT queries** on both PostgreSQL and MySQL databases
- **Automatic LIMIT enforcement** for safety (max 1000 rows)
- **Real-time query results** displayed in paginated tables
- **Query validation** to prevent non-SELECT statements (INSERT/UPDATE/DELETE blocked)
- **Database-specific syntax support** (PostgreSQL and MySQL dialects)
- **Execution timing** and row count metrics
- **Keyboard shortcut** (Ctrl/Cmd + Enter) for quick execution

### 🤖 User Story 3: Natural Language to SQL
- **AI-powered SQL generation** using OpenAI GPT models
- **Database-aware prompts** - generates PostgreSQL or MySQL syntax based on database type
- **Schema-aware prompts** that include table/column information
- **SQL explanations** for generated queries
- **One-click execution** of generated SQL

### 📥 User Story 4: Query Results Export
- **Multi-format export** - Download query results in CSV, JSON, or Excel formats
- **CSV Export** - UTF-8 encoded with BOM for Excel compatibility, proper escaping for special characters
- **JSON Export** - Pretty-printed with type preservation, ISO 8601 dates, Unicode support
- **Excel Export** - Native XLSX format with type-based cell formatting (numbers, dates, booleans)
- **Smart column handling** - Automatic disambiguation of duplicate column names
- **Large dataset support** - Up to 100,000 rows per export with validation
- **Streaming downloads** - No server-side file storage, direct browser downloads
- **Timestamped filenames** - Format: `{database}_{timestamp}.{extension}`

## Tech Stack

### Backend
- **Python 3.11+** with type hints
- **FastAPI 0.124+** for REST API
- **Pydantic 2.12+** with camelCase serialization
- **PostgreSQL** via psycopg2-binary
- **MySQL** via mysql-connector-python 8.2+
- **SQLite** for metadata storage
- **sqlparse** for SQL validation
- **OpenAI API** for natural language processing
- **openpyxl 3.1+** for Excel file generation

### Frontend
- **React 18.3** with TypeScript
- **Refine v6** for admin UI framework
- **Ant Design 5.24** for UI components
- **Tailwind CSS 4** for styling
- **Monaco Editor** for code editing
- **Vite** for build tooling
- **Axios** for API communication

## Project Structure

```
db-query/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── api/v1/            # REST API endpoints
│   │   │   ├── databases.py   # Database CRUD + metadata
│   │   │   ├── queries.py     # Query execution + NL conversion
│   │   │   └── exports.py     # Query results export
│   │   ├── models/            # Pydantic models
│   │   │   ├── database.py    # Connection models
│   │   │   ├── metadata.py    # Schema metadata models
│   │   │   ├── query.py       # Query request/response models
│   │   │   ├── export.py      # Export request/format models
│   │   │   └── errors.py      # Error response models
│   │   ├── services/          # Business logic
│   │   │   ├── db_connection.py      # PostgreSQL connection
│   │   │   ├── metadata_extractor.py # Schema extraction
│   │   │   ├── query_executor.py     # SQL execution
│   │   │   ├── nl_converter.py       # Natural language to SQL
│   │   │   ├── storage.py            # SQLite operations
│   │   │   └── export/               # Export services
│   │   │       ├── base.py           # Base exporter class
│   │   │       ├── csv_exporter.py   # CSV export
│   │   │       ├── json_exporter.py  # JSON export
│   │   │       └── excel_exporter.py # Excel export
│   │   ├── utils/             # Utilities
│   │   │   ├── camel_case.py  # CamelCase conversion
│   │   │   ├── sql_validator.py # SQL validation
│   │   │   └── filename.py    # Filename sanitization
│   │   └── main.py            # FastAPI app configuration
│   ├── tests/                 # Test scripts
│   └── pyproject.toml         # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── SchemaTree.tsx      # Database schema tree
│   │   │   ├── ColumnDetails.tsx   # Column metadata panel
│   │   │   ├── SqlEditor.tsx       # Monaco SQL editor
│   │   │   ├── QueryResults.tsx    # Results table
│   │   │   └── ExportButton.tsx    # Export dropdown button
│   │   ├── pages/             # Page components
│   │   │   ├── DatabaseList.tsx # Database management
│   │   │   └── QueryTool.tsx    # Query execution UI
│   │   ├── services/          # API client
│   │   │   └── api.ts         # Axios HTTP client
│   │   ├── types/             # TypeScript types
│   │   │   ├── database.ts
│   │   │   ├── query.ts
│   │   │   └── export.ts
│   │   └── App.tsx            # Root component with routing
│   └── package.json           # Node dependencies
├── db-query/                  # SQLite database directory
│   └── db_query.db           # Metadata storage
├── Makefile                   # Development commands
├── test.rest                  # API testing file
└── README.md                  # This file
```

## Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **PostgreSQL database** (for connecting to)
- **OpenAI API key** (for natural language features)

## Installation

### Quick Start (Using Makefile)

```bash
# Install all dependencies (backend + frontend)
make install

# Initialize SQLite database
make db-init

# Start development servers (backend + frontend in parallel)
make dev
```

### Manual Installation

#### Backend Setup

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
cd backend
pip install -e .
```

#### Frontend Setup

```bash
cd frontend
npm install
```

#### Environment Configuration

Create a `.env` file in the project root:

```bash
# Backend Configuration
SQLITE_DB_PATH=db-query/db_query.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# OpenAI Configuration (for natural language features)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Usage

### Start Development Servers

#### Option 1: Use Makefile (Recommended)

```bash
# Start both backend and frontend
make dev

# Or start individually
make backend   # Backend only (http://127.0.0.1:8000)
make frontend  # Frontend only (http://localhost:5173)
```

#### Option 2: Manual Start

```bash
# Terminal 1: Start backend
cd backend
../.venv/bin/python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

### Testing

#### Backend Tests

```bash
# Run database connection tests
cd backend/tests
python test_db_connection.py
```

#### API Testing with REST Client

Open `test.rest` in VS Code with the REST Client extension to test all API endpoints interactively.

## API Endpoints

### Database Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/databases/` | Create database connection |
| GET | `/api/v1/databases/` | List all connections |
| PUT | `/api/v1/databases/{db_name}/` | Update connection URL |
| DELETE | `/api/v1/databases/{db_name}/` | Delete connection |
| GET | `/api/v1/databases/{db_name}/metadata/` | Get schema metadata |

### Query Execution

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/databases/{db_name}/query/` | Execute SQL query |
| POST | `/api/v1/databases/{db_name}/nl-query/` | Generate SQL from natural language |
| POST | `/api/v1/databases/{db_name}/export/` | Export query results (CSV/JSON/Excel) |

### Health Checks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/api/v1/health` | API health check |

## Development Commands

The `Makefile` provides convenient commands for common tasks:

```bash
# Installation
make install           # Install all dependencies
make install-backend   # Install backend only
make install-frontend  # Install frontend only

# Development
make dev              # Start both servers in parallel
make backend          # Start backend server
make frontend         # Start frontend server

# Database
make db-init          # Initialize SQLite database
make db-reset         # Reset database (drop and recreate)

# Testing
make test             # Run all tests
make health           # Test backend health endpoint

# Code Quality
make lint             # Run linters (backend + frontend)
make format           # Format code (black + prettier)

# Build
make build            # Build frontend for production
make build-backend    # Build backend wheel

# Cleanup
make clean            # Remove build artifacts
make clean-all        # Remove all generated files
```

## Architecture

### Backend Architecture

- **REST API Layer** (`api/v1/`): FastAPI routers with Pydantic validation
- **Service Layer** (`services/`): Business logic and external integrations
- **Data Layer** (`models/` + `storage.py`): Pydantic models and SQLite operations
- **Utilities** (`utils/`): Shared helpers (camelCase, SQL validation)

### Frontend Architecture

- **Refine Framework**: Provides routing, state management, and UI patterns
- **Component-Based**: Reusable components for schema browsing and query execution
- **Type-Safe API Client**: Axios with TypeScript interfaces
- **Responsive Design**: Tailwind CSS for mobile-friendly layouts

### Data Flow

1. **Connection Management**: User creates connection → Validated → Tested → Stored in SQLite → Metadata extracted and cached
2. **Query Execution**: User writes SQL → Validated (SELECT only) → LIMIT added if missing → Executed → Results paginated
3. **Natural Language**: User enters prompt → Schema context added → OpenAI generates SQL → User reviews → Execute
4. **Export Results**: User clicks Export → Selects format (CSV/JSON/Excel) → Data exported with type preservation → Browser download triggered

## Security Features

- ✅ **SQL Injection Prevention**: Only SELECT queries allowed, parameterized queries for metadata
- ✅ **CORS Configuration**: Whitelist-based origin control
- ✅ **Connection String Validation**: PostgreSQL URL format enforcement
- ✅ **Query Limits**: Automatic LIMIT clause to prevent large result sets
- ✅ **Export Limits**: Maximum 100,000 rows per export to prevent resource exhaustion
- ✅ **Filename Sanitization**: Unsafe characters removed from generated filenames
- ✅ **Error Sanitization**: Generic error messages to avoid information leakage

## Configuration

### Backend Configuration

Edit `.env` or environment variables:

- `SQLITE_DB_PATH`: Path to metadata database (default: `db-query/db_query.db`)
- `CORS_ORIGINS`: Comma-separated allowed origins (default: `http://localhost:5173,http://localhost:3000`)
- `OPENAI_API_KEY`: OpenAI API key for natural language features
- `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4o-mini`)

### Frontend Configuration

Edit `frontend/vite.config.ts` to change:
- Development server port (default: 5173)
- API proxy settings
- Build output directory

## Troubleshooting

### Backend Issues

**Problem**: Module import errors
```bash
# Solution: Install backend in editable mode
cd backend && pip install -e .
```

**Problem**: Database connection fails
```bash
# Solution: Test connection URL format
# Must start with postgresql:// or postgres://
postgresql://user:password@host:port/database
```

### Frontend Issues

**Problem**: CORS errors
```bash
# Solution: Check backend CORS_ORIGINS includes frontend URL
# Default: http://localhost:5173
```

**Problem**: Build fails with Tailwind CSS errors
```bash
# Solution: Ensure @tailwindcss/postcss is installed
cd frontend && npm install @tailwindcss/postcss
```

## Contributing

1. Follow Python PEP 8 style guide for backend code
2. Use TypeScript strict mode for frontend code
3. Add type hints to all Python functions
4. Write tests for new features
5. Update API documentation in `test.rest`

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **Refine**: React-based framework for admin applications
- **FastAPI**: Modern Python web framework
- **Ant Design**: Enterprise-class UI components
- **Monaco Editor**: VS Code's text editor component
- **OpenAI**: GPT models for natural language processing
