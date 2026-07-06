import os
import sqlite3

import pytest

from src.memory import create_memory_connection


def test_create_memory_connection_creates_sqlite_connection(tmp_path):
    db_path = tmp_path / "memory_test.db"
    conn = create_memory_connection(str(db_path))
    try:
        assert isinstance(conn, sqlite3.Connection)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)")
        cursor.execute("INSERT INTO test_table (value) VALUES ('hello')")
        conn.commit()
        cursor.execute("SELECT value FROM test_table WHERE id = 1")
        assert cursor.fetchone()[0] == "hello"
    finally:
        conn.close()
