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

    # Split the SQL file into individual statements (splitting by semicolon)
    # This is a simple approach and might not work for complex SQL
    statements = sql.split(';')

    # Execute each statement
    for statement in statements:
        statement = statement.strip()
        if statement:  # Skip empty statements
            print(f"Executing statement: {statement[:80]}...")  # Print first 80 chars of statement
            try:
                db.client.postgrest.from_("rpc").select("*").execute()  # Test connection first

                # Execute raw SQL
                result = db.client.postgrest.rpc('exec_sql', {'query': statement}).execute()
                print(f"Statement executed successfully.")
                time.sleep(1)  # Small delay to avoid overwhelming the database
            except Exception as e:
                print(f"Error executing statement: {e}")
                # Continue with other statements even if one fails

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_migration.py <migration_file>")
        sys.exit(1)

    migration_file = sys.argv[1]
    if not os.path.exists(migration_file):
        print(f"Error: Migration file {migration_file} not found.")
        sys.exit(1)

    execute_migration(migration_file)