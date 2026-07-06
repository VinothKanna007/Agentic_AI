import sqlite3


def create_memory_connection(db_path: str = "sql_agent_memory.db") -> sqlite3.Connection:
    return sqlite3.connect(db_path, check_same_thread=False)
