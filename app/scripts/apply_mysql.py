import os
import sys
import pathlib

# Ensure app root in path
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.utils.mysql_db import get_mysql_connection


def run_sql_file(cursor, path: str):
    with open(path, 'r') as f:
        sql = f.read()

    # Split on semicolons while respecting potential delimiter content
    # For our simple schema/seed files, splitting on ';' is sufficient
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        cursor.execute(stmt)


def main():
    schema_path = os.path.join(ROOT, 'app', 'scripts', 'mysql_schema.sql')
    seed_path = os.path.join(ROOT, 'app', 'scripts', 'mysql_seed.sql')

    # Connect to server without requiring the target DB to exist yet
    conn = get_mysql_connection({"database": "mysql"})
    cur = conn.cursor()

    print("Applying MySQL schema...")
    run_sql_file(cur, schema_path)
    print("Schema applied.")

    print("Seeding MySQL data...")
    run_sql_file(cur, seed_path)
    print("Seed data applied.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()


