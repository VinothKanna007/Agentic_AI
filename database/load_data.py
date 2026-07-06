import csv
import os
import sys
from pathlib import Path
import mysql.connector
from mysql.connector import Error

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILE = Path(__file__).resolve().parent / "mysql_schema.sql"
DATA_DIR = ROOT / "data"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_env

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = get_env("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "retail_agent_assignment")

TABLE_FILES = {
    "stores": "stores.csv",
    "products": "products.csv",
    "customers": "customers.csv",
    "sales_transactions": "sales_transactions.csv",
    "returns": "returns.csv",
}


def execute_schema(cursor):
    sql_text = SCHEMA_FILE.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    for statement in statements:
        cursor.execute(statement)


def load_csv(cursor, table_name: str, csv_path: Path) -> int:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        headers = next(reader)
        columns = ", ".join(f"`{col}`" for col in headers)
        placeholders = ", ".join(["%s"] * len(headers))
        insert_sql = f"INSERT IGNORE INTO `{table_name}` ({columns}) VALUES ({placeholders})"

        row_count = 0
        for row in reader:
            if len(row) != len(headers):
                raise ValueError(
                    f"Row length mismatch in {csv_path.name}: expected {len(headers)}, got {len(row)}"
                )
            cursor.execute(insert_sql, row)
            row_count += 1

    return row_count


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        autocommit=True,
    )

    try:
        with conn.cursor() as cursor:
            execute_schema(cursor)
            print(f"Schema applied from {SCHEMA_FILE}")

            cursor.execute(f"USE `{MYSQL_DATABASE}`")

            final_counts = {}
            for table_name, file_name in TABLE_FILES.items():
                csv_path = DATA_DIR / file_name
                if not csv_path.exists():
                    raise FileNotFoundError(f"Missing csv file for table {table_name}: {csv_path}")

                loaded = load_csv(cursor, table_name, csv_path)
                final_counts[table_name] = loaded
                print(f"Loaded {loaded} rows into {table_name}")

            print("\nRow counts loaded from CSV files:")
            for table_name, count in final_counts.items():
                print(f"- {table_name}: {count}")

    except Error as exc:
        raise RuntimeError(f"MySQL error: {exc}") from exc
    finally:
        conn.close()


if __name__ == "__main__":
    main()
