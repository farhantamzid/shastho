## MySQL-backed Regulatory Dashboard (Local Only)

This project primarily uses Supabase. For the regulatory dashboard demo, we added a small MySQL-backed data path to simulate fetching metrics from a separate MySQL database. This is intended to support migration demonstrations (e.g., EC2 -> private MySQL subnet). It does not replace Supabase usage elsewhere.

Setup

1. Install MySQL locally and ensure you know your MySQL root/user credentials.
2. Create a `.env` file in the project root with:

```
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=<your_user>
MYSQL_PASSWORD=<your_password>
MYSQL_DB=shastho_regulatory
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Apply schema and seed data to MySQL:

```
python app/scripts/apply_mysql.py
```

5. Run the Flask app as usual. Visit:

```
http://127.0.0.1:5001/regulatory/dashboard
```

Data Flow

- `app/services/regulatory_service.py` fetches dashboard data from MySQL using `app/utils/mysql_db.py`.
- The schema and data live in `app/scripts/mysql_schema.sql` and `app/scripts/mysql_seed.sql`.
- Only the regulatory dashboard path uses MySQL; all other features continue using Supabase.
