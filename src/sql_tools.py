import os
import mysql.connector
from typing import Any, Dict, List
from langchain_core.tools import tool

from src.safety import validate_sql_string


def get_db_connection() -> mysql.connector.connection.MySQLConnection:
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE", "retail_agent_assignment"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "Root@123"),
        autocommit=True,
    )


@tool
def get_schema() -> str:
    """Return a readable schema description for all tables in the current database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
        )
        tables = [row[0] for row in cursor.fetchall()]

        schema_lines = []
        for table in tables:
            cursor.execute(
                "SELECT column_name, column_type, is_nullable, column_key "
                "FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = %s "
                "ORDER BY ordinal_position",
                (table,),
            )
            rows = cursor.fetchall()
            cols = []
            for name, ctype, nullable, key in rows:
                column_parts = [name, ctype]
                if nullable == "NO":
                    column_parts.append("NOT NULL")
                if key == "PRI":
                    column_parts.append("PK")
                cols.append(" ".join(column_parts))
            schema_lines.append(f"{table}({', '.join(cols)})")

        return "\n".join(schema_lines)
    finally:
        conn.close()


@tool
def execute_sql(query: str) -> List[Dict[str, Any]]:
    """Execute a safe SELECT query and return rows as dictionaries."""
    safe_query = validate_sql_string(query)
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(safe_query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()
