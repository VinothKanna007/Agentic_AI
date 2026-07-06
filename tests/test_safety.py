import pytest

from src.safety import validate_sql_string


@pytest.mark.parametrize(
    ("sql", "expected"),
    [
        ("SELECT * FROM stores", "SELECT * FROM stores"),
        ("  SELECT store_id, store_name FROM stores  ", "SELECT store_id, store_name FROM stores"),
        ("SELECT store_id FROM sales_transactions;", "SELECT store_id FROM sales_transactions"),
    ],
)
def test_validate_sql_string_accepts_safe_select(sql, expected):
    assert validate_sql_string(sql) == expected


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO stores (store_id) VALUES ('ST-001')",
        "UPDATE stores SET store_name = 'x'",
        "DELETE FROM stores WHERE store_id = 'ST-001'",
        "DROP TABLE stores",
        "ALTER TABLE stores ADD COLUMN x INT",
        "TRUNCATE TABLE stores",
        "CREATE TABLE x (id INT)",
        "REPLACE INTO stores (store_id) VALUES ('ST-001')",
    ],
)
def test_validate_sql_string_rejects_non_select_statements(sql):
    with pytest.raises(ValueError, match="Only SELECT queries are allowed."):
        validate_sql_string(sql)


def test_validate_sql_string_rejects_select_with_blocked_keyword():
    with pytest.raises(ValueError, match="Destructive or write SQL is blocked."):
        validate_sql_string("SELECT * FROM stores WHERE notes LIKE 'drop'")


def test_validate_sql_string_rejects_multiple_statements():
    with pytest.raises(ValueError, match="Multiple SQL statements are not allowed."):
        validate_sql_string("SELECT * FROM stores; SELECT * FROM sales_transactions")


def test_validate_sql_string_rejects_non_select():
    with pytest.raises(ValueError, match="Only SELECT queries are allowed."):
        validate_sql_string("SHOW TABLES")


def test_validate_sql_string_requires_from_clause():
    with pytest.raises(ValueError, match="FROM clause"):
        validate_sql_string("SELECT 1")
