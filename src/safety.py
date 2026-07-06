from langchain_core.tools import tool
import re

BLOCKED = [
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "replace",
]


def validate_sql_string(sql: str) -> str:
    """Validate a SQL string to ensure it is a safe, single `SELECT` query."""
    cleaned = sql.strip().lower()
    if not cleaned.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    if ";" in cleaned.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")
    if any(re.search(rf"\b{word}\b", cleaned) for word in BLOCKED):
        raise ValueError("Destructive or write SQL is blocked.")
    if not re.search(r"\bfrom\b", cleaned):
        raise ValueError("SELECT queries must include a FROM clause and query a real table.")
    return sql.strip().rstrip(";")

# Expose the validator as a tool for the agent runtime. This avoids
# duplicating docstrings while keeping the internal implementation
# available as `validate_sql_string` for direct calls.
validate_sql = tool(validate_sql_string)
