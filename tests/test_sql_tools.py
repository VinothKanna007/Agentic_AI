import os

import pytest

from src import sql_tools
from src.safety import validate_sql_string


@pytest.fixture(autouse=True)
def mysql_env(monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", os.getenv("MYSQL_HOST", "localhost"))
    monkeypatch.setenv("MYSQL_PORT", os.getenv("MYSQL_PORT", "3306"))
    monkeypatch.setenv("MYSQL_DATABASE", os.getenv("MYSQL_DATABASE", "retail_agent_assignment"))
    monkeypatch.setenv("MYSQL_USER", os.getenv("MYSQL_USER", "root"))
    monkeypatch.setenv("MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", ""))


def invoke_tool(tool, payload):
    if hasattr(tool, "invoke"):
        return tool.invoke(payload)
    return tool(**payload)


def test_get_db_connection_connects_successfully():
    conn = sql_tools.get_db_connection()
    try:
        assert conn.is_connected()
    finally:
        conn.close()


def test_execute_sql_returns_rows_for_safe_query():
    rows = invoke_tool(sql_tools.execute_sql, {"query": "SELECT store_id FROM stores LIMIT 1"})
    assert isinstance(rows, list)
    assert len(rows) >= 0
    if rows:
        assert "store_id" in rows[0]


def test_execute_sql_rejects_unsafe_query():
    with pytest.raises(ValueError, match="Only SELECT queries are allowed."):
        invoke_tool(sql_tools.execute_sql, {"query": "DROP TABLE stores"})


def test_validate_sql_string_returns_cleaned_query():
    assert validate_sql_string("SELECT store_id FROM stores; ") == "SELECT store_id FROM stores"
