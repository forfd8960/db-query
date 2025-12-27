"""Natural language to SQL conversion service using OpenAI."""

import os
from typing import Optional

from openai import OpenAI

from src.models.query import NaturalLanguageQueryResponse
from src.services.metadata_extractor import metadata_extractor


class NaturalLanguageConverter:
    """Service for converting natural language to SQL using OpenAI."""

    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    async def convert_to_sql(
        self, url: str, connection_id: int, prompt: str, database_type: str = "postgresql"
    ) -> NaturalLanguageQueryResponse:
        """
        Convert natural language prompt to SQL query.

        Args:
            url: Database connection URL
            connection_id: Database connection ID
            prompt: Natural language query
            database_type: Type of database ("postgresql" or "mysql")

        Returns:
            NaturalLanguageQueryResponse with SQL and explanation

        Raises:
            Exception: If OpenAI API call fails
        """
        # Get database metadata
        metadata = metadata_extractor.extract_metadata(url, connection_id)

        # Build schema context
        schema_context = self._build_schema_context(metadata)

        # Build system prompt based on database type
        if database_type == "mysql":
            system_prompt = self._build_mysql_system_prompt(schema_context)
        else:
            system_prompt = self._build_postgres_system_prompt(schema_context)

        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=1000,
            )

            # Parse response
            content = response.choices[0].message.content
            sql, explanation = self._parse_response(content)

            return NaturalLanguageQueryResponse(sql=sql, explanation=explanation)

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _build_postgres_system_prompt(self, schema_context: str) -> str:
        """Build system prompt for PostgreSQL."""
        return f\"\"\"You are a PostgreSQL SQL expert. Generate a valid SQL SELECT query based on the user's natural language request.

Database Schema:
{schema_context}

Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper PostgreSQL syntax
3. Use schema-qualified table names (schema.table)
4. Return the SQL query and a brief explanation
5. If the request is ambiguous, make reasonable assumptions
6. Do not add LIMIT clause (it will be added automatically)

Response format:
SQL: <your sql query>
Explanation: <brief explanation of what the query does>
\"\"\"

    def _build_mysql_system_prompt(self, schema_context: str) -> str:
        \"\"\"Build system prompt for MySQL.\"\"\"
        return f\"\"\"You are a MySQL SQL expert. Generate a valid SQL SELECT query based on the user's natural language request.

Database Schema:
{schema_context}

Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper MySQL syntax and functions (NOW(), CURDATE(), DATE_ADD(), CONCAT(), etc.)
3. Use backticks for identifiers if needed (e.g., `table_name`, `column_name`)
4. Use database.table notation for table names
5. Return the SQL query and a brief explanation
6. If the request is ambiguous, make reasonable assumptions
7. Do not add LIMIT clause (it will be added automatically)
8. Use MySQL-specific date/time functions, NOT PostgreSQL functions

MySQL-specific examples:
- Current date: CURDATE() (not CURRENT_DATE)
- Current timestamp: NOW() (not CURRENT_TIMESTAMP)
- Date arithmetic: DATE_ADD(), DATE_SUB(), DATEDIFF()
- String concatenation: CONCAT()

Response format:
SQL: <your sql query>
Explanation: <brief explanation of what the query does>
\"\"\"

    def _build_schema_context(self, metadata) -> str:
        """Build schema context string for OpenAI prompt."""
        lines = []

        for table in metadata.tables:
            # Table header
            lines.append(f"\nTable: {table.schema_name}.{table.name}")
            if table.row_count is not None:
                lines.append(f"Rows: {table.row_count}")

            # Columns
            lines.append("Columns:")
            for col in table.columns:
                pk_marker = " (PRIMARY KEY)" if col.is_primary_key else ""
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                default = f" DEFAULT {col.column_default}" if col.column_default else ""
                lines.append(f"  - {col.name}: {col.data_type} {nullable}{default}{pk_marker}")

        return "\n".join(lines)

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse OpenAI response to extract SQL and explanation."""
        lines = content.strip().split("\n")

        sql = ""
        explanation = ""

        for line in lines:
            line = line.strip()
            if line.startswith("SQL:"):
                sql = line[4:].strip()
            elif line.startswith("Explanation:"):
                explanation = line[12:].strip()
            elif sql and not line.startswith("SQL:") and not line.startswith("Explanation:"):
                # Continue SQL from previous line
                if not explanation:
                    sql += " " + line
                else:
                    explanation += " " + line

        # Clean up SQL (remove markdown code blocks if present)
        sql = sql.replace("```sql", "").replace("```", "").strip()

        if not sql:
            raise ValueError("Failed to parse SQL from OpenAI response")

        if not explanation:
            explanation = "SQL query generated from natural language"

        return sql, explanation


# Global instance (lazy initialization)
_nl_converter: Optional[NaturalLanguageConverter] = None


def get_nl_converter() -> NaturalLanguageConverter:
    """Get or create NaturalLanguageConverter instance."""
    global _nl_converter
    if _nl_converter is None:
        _nl_converter = NaturalLanguageConverter()
    return _nl_converter


# Alias for convenience
nl_converter = get_nl_converter()
