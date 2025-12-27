"""SQL validation utilities using sqlparse."""

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword


class SQLValidator:
    """SQL validation service."""

    def validate_select_only(self, sql: str) -> tuple[bool, str | None]:
        """
        Validate that SQL contains only SELECT statements.

        Args:
            sql: SQL query string

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Parse SQL
        try:
            statements = sqlparse.parse(sql)
        except Exception as e:
            return (False, f"Invalid SQL syntax: {e}")

        if not statements:
            return (False, "Empty SQL query")

        # Check each statement
        for statement in statements:
            if not self._is_select_statement(statement):
                return (False, "Only SELECT queries are allowed")

        return (True, None)

    def _is_select_statement(self, statement: Statement) -> bool:
        """Check if a statement is a SELECT query."""
        # Get the statement type - sqlparse identifies the first DML/DDL keyword
        first_keyword = None
        
        for token in statement.tokens:
            # Skip whitespace, comments, and newlines
            if token.ttype in (sqlparse.tokens.Whitespace, sqlparse.tokens.Comment, sqlparse.tokens.Newline):
                continue
            
            # Check if it's a keyword token
            if token.ttype is sqlparse.tokens.Keyword.DML:
                first_keyword = token.value.upper()
                break
            elif token.ttype is sqlparse.tokens.Keyword:
                first_keyword = token.value.upper()
                break
        
        # Return True only if it's a SELECT statement
        return first_keyword == "SELECT"

    def add_limit_if_missing(self, sql: str, max_limit: int = 1000) -> str:
        """
        Add LIMIT clause if missing from SQL query.

        Args:
            sql: SQL query string
            max_limit: Maximum number of rows to return

        Returns:
            SQL with LIMIT clause
        """
        # Parse and format SQL
        parsed = sqlparse.parse(sql)
        if not parsed:
            return sql

        statement = parsed[0]

        # Check if LIMIT already exists
        has_limit = any(
            token.ttype is Keyword and "LIMIT" in token.value.upper() for token in statement.flatten()
        )

        if has_limit:
            return sql

        # Add LIMIT clause
        sql_stripped = sql.rstrip().rstrip(";")
        return f"{sql_stripped} LIMIT {max_limit};"


# Global instance
sql_validator = SQLValidator()
