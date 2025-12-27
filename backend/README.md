# DB Query Tool Backend

FastAPI backend for the Database Query Tool.

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Create .env file
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run server
uvicorn src.main:app --reload
```

## API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
