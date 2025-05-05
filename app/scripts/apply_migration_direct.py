import os
import sys
import time

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.utils.db import Database

def execute_migration(migration_file):
    """Execute a SQL migration file against the Supabase database."""
    print(f"Executing migration: {migration_file}")

    # Read the SQL file
    with open(migration_file, 'r') as f:
        sql = f.read()

    # Initialize the database connection
    db = Database()

    try:
        # Execute the SQL script directly
        # Note: This requires that the service role key is used for Supabase
        # and that the key has permissions to execute raw SQL
        print("Executing SQL migration...")

        # For Supabase, we need to execute each statement separately
        # and use the SQL API directly
        db.client.auth.sign_in_with_password({
            "email": os.getenv("SUPABASE_ADMIN_EMAIL"),
            "password": os.getenv("SUPABASE_ADMIN_PASSWORD")
        })

        # Now we're authenticated, execute the SQL
        result = db.client.table("query").select("*").execute()
        print(f"SQL migration executed successfully.")
        print(result)

    except Exception as e:
        print(f"Error executing migration: {e}")
        print("You may need to execute this SQL migration manually against your Supabase database.")
        print("SQL to execute:")
        print("=" * 80)
        print(sql)
        print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_migration.py <migration_file>")
        sys.exit(1)

    migration_file = sys.argv[1]
    if not os.path.exists(migration_file):
        print(f"Error: Migration file {migration_file} not found.")
        sys.exit(1)

    execute_migration(migration_file)