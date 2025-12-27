# Quickstart Guide: Database Query Tool

**Purpose**: Get the database query tool running locally in under 10 minutes.  
**Date**: 2025-12-16  
**Audience**: Developers setting up the tool for the first time

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([python.org](https://python.org))
- **Node.js 18+** and npm installed ([nodejs.org](https://nodejs.org))
- **PostgreSQL database** accessible for testing (local or remote)
- **OpenAI API key** for natural language query features ([platform.openai.com](https://platform.openai.com/api-keys))
- **Git** for cloning the repository

## Architecture Overview

The application consists of two parts:

- **Backend**: FastAPI server (Python) on `http://localhost:8000`
- **Frontend**: React app (TypeScript) on `http://localhost:5173`
- **Storage**: SQLite database at `./db-query/db_query.db` (created automatically)

```
┌─────────────┐      HTTP      ┌──────────────┐      SQL       ┌────────────┐
│   Browser   │ ←────────────→ │    FastAPI   │ ←────────────→ │ PostgreSQL │
│  (React)    │   REST API     │   (Python)   │   Queries      │  (User DB) │
└─────────────┘                └──────────────┘                └────────────┘
                                      ↕
                                   SQLite
                                 (Metadata)
```

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd db-query
git checkout 001-db-query-tool
```

## Step 2: Backend Setup

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Create Python Virtual Environment

**Option A: Using uv (recommended)**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Option B: Using standard venv**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2.3 Install Dependencies

**With uv:**
```bash
uv pip install -r requirements.txt
```

**With pip:**
```bash
pip install -r requirements.txt
```

**Expected dependencies:**
- fastapi
- uvicorn[standard]
- pydantic
- sqlparse
- sqlglot
- openai
- psycopg2-binary
- python-dotenv

### 2.4 Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**.env file contents:**
```env
# OpenAI API Key (required for natural language queries)
OPENAI_API_KEY=sk-your-api-key-here

# Database storage path (optional, defaults to ./db-query/db_query.db)
SQLITE_DB_PATH=../db-query/db_query.db

# CORS origins (optional, defaults to allow all for development)
CORS_ORIGINS=*

# Server configuration (optional)
HOST=0.0.0.0
PORT=8000
```

### 2.5 Start Backend Server

```bash
uvicorn src.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend is running:**
- Open browser to `http://localhost:8000/docs` (Swagger UI)
- You should see the API documentation

**Leave this terminal running** and open a new terminal for frontend setup.

## Step 3: Frontend Setup

### 3.1 Navigate to Frontend Directory

```bash
# In a new terminal
cd frontend
```

### 3.2 Install Dependencies

```bash
npm install
```

**Expected dependencies:**
- react
- react-dom
- typescript
- @refinedev/core
- @refinedev/antd
- antd
- tailwindcss
- @monaco-editor/react
- axios

### 3.3 Configure Backend API URL (if needed)

Frontend is pre-configured to use `http://localhost:8000/api/v1`. If your backend runs on a different port, edit `frontend/src/services/api.ts`:

```typescript
const API_BASE = 'http://localhost:8000/api/v1';  // Change port if needed
```

### 3.4 Start Frontend Development Server

```bash
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Open browser to `http://localhost:5173`** - you should see the database query tool interface!

## Step 4: First Database Connection

### 4.1 Prepare Test Database

If you don't have a PostgreSQL database ready, create one:

```bash
# Using psql or pgAdmin, create a test database
createdb test_db

# Create sample table (optional)
psql test_db -c "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP DEFAULT NOW());"
psql test_db -c "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com');"
```

### 4.2 Add Database Connection in UI

1. In the browser, click **"Add Database"** or navigate to database management
2. Enter PostgreSQL connection URL:
   ```
   postgresql://username:password@localhost:5432/test_db
   ```
3. Click **"Connect"**

**Expected behavior:**
- Connection URL is validated
- Backend connects to PostgreSQL
- Metadata is extracted (tables, columns)
- Database appears in left sidebar tree

### 4.3 Browse Schema

1. Click on database name in sidebar to expand
2. See list of tables and views
3. Click on a table (e.g., "users")
4. Right panel shows column information (name, data type, nullable, etc.)

## Step 5: Execute Your First Query

### 5.1 Write SQL Query

1. Select a table from the sidebar (e.g., "users")
2. In the SQL editor (Monaco editor in center panel), type:
   ```sql
   SELECT * FROM users
   ```
3. Click **"Execute"** button

**Expected behavior:**
- Query is validated (syntax check, SELECT-only enforcement)
- Automatic LIMIT 1000 is added
- Results appear in table below editor
- Table shows columns: id, name, email, createdAt (camelCase)

### 5.2 Test Validation

Try entering a non-SELECT statement:
```sql
UPDATE users SET name = 'Charlie' WHERE id = 1
```

Click **"Execute"**

**Expected behavior:**
- Error message: "Only SELECT statements are allowed"
- Query is blocked from execution

## Step 6: Try Natural Language Query

### 6.1 Enter Natural Language

1. Switch to **"Natural Language"** tab or input field
2. Type: `Show me all users created in the last 7 days`
3. Click **"Generate SQL"**

**Expected behavior:**
- Backend sends request to OpenAI API
- LLM generates SQL query (e.g., `SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'`)
- Generated SQL appears in the editor
- User can review and edit before executing

### 6.2 Execute Generated SQL

1. Review the generated SQL
2. Make edits if needed
3. Click **"Execute"** to run the query
4. Results appear in table below

## Common Issues & Solutions

### Issue: Backend fails to start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate  # Activate venv
pip install -r requirements.txt
```

---

### Issue: Cannot connect to PostgreSQL

**Error:** `connection to server at "localhost", port 5432 failed`

**Solution:** 
- Verify PostgreSQL is running: `pg_ctl status` or `sudo systemctl status postgresql`
- Check connection URL format: `postgresql://user:password@host:port/database`
- Verify credentials and database exists

---

### Issue: Natural language queries fail

**Error:** `OpenAI API error: 401 Unauthorized`

**Solution:** 
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Check API key is valid at [platform.openai.com](https://platform.openai.com/api-keys)
- Ensure API key has credits available

---

### Issue: CORS errors in browser console

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
- Verify backend is running on `http://localhost:8000`
- Check `CORS_ORIGINS` in backend `.env` allows frontend origin
- Restart backend after changing `.env`

---

### Issue: Frontend cannot fetch data

**Error:** `Network Error` or `Failed to fetch`

**Solution:**
- Verify backend is running (`http://localhost:8000/docs` should work)
- Check `API_BASE` URL in `frontend/src/services/api.ts` matches backend
- Check browser DevTools Network tab for specific error

## Next Steps

Now that you're up and running:

1. **Add Multiple Databases**: Connect to different PostgreSQL instances
2. **Explore Schema**: Browse tables, views, and column details
3. **Write Queries**: Practice SQL queries with auto-LIMIT safety
4. **Try Complex Queries**: Joins, aggregations, subqueries (all SELECT-only)
5. **Use Natural Language**: Experiment with different query descriptions
6. **Check Metadata Cache**: Notice faster loading on subsequent access

## Development Workflow

### Running Tests

**Backend tests:**
```bash
cd backend
pytest tests/
```

**Frontend tests:**
```bash
cd frontend
npm test
```

### Code Quality

**Backend linting:**
```bash
cd backend
ruff check src/  # or flake8, black
mypy src/
```

**Frontend linting:**
```bash
cd frontend
npm run lint
npm run type-check
```

### Rebuilding Metadata Cache

If database schema changes, refresh metadata:
1. In UI, click **"Refresh Metadata"** button next to database name
2. Or via API: `GET /api/v1/databases/{db_name}/metadata/?refresh=true`

## Security Warnings

⚠️ **This tool is for development/internal use only:**

- **No authentication**: Anyone with access to the UI can query any connected database
- **Credentials stored in plaintext**: Connection URLs (with passwords) stored in SQLite
- **CORS open by default**: Backend accepts requests from any origin

**Recommended practices:**
- Use **read-only PostgreSQL credentials** for connections
- Run on **localhost only** or secured network
- Do not expose backend to public internet
- Consider using **environment variables** for sensitive connection URLs

## API Documentation

Full API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: [contracts/api.yaml](contracts/api.yaml)

## Architecture References

- **Feature Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Data Models**: [data-model.md](data-model.md)
- **Research & Decisions**: [research.md](research.md)

## Support

For issues or questions:
1. Check [Common Issues](#common-issues--solutions) above
2. Review error messages in browser DevTools and backend terminal
3. Consult API documentation at `/docs`
4. Check constitution principles in [.specify/memory/constitution.md](../.specify/memory/constitution.md)

**Happy querying! 🚀**
