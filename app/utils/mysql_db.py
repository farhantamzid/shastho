"""
MySQL connection helper for the Shastho Flask application.
---------------------------------------------------------
This module provides a simple helper to connect to a local MySQL database
for the regulatory dashboard. It does not replace Supabase; it's scoped
only to the regulatory analytics demo.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import MySQLConnection


load_dotenv()


def get_mysql_connection(overrides: Optional[Dict[str, Any]] = None) -> MySQLConnection:
    """
    Create and return a MySQL connection using env vars or provided overrides.

    Environment variables used:
      - MYSQL_HOST (default: 127.0.0.1)
      - MYSQL_PORT (default: 3306)
      - MYSQL_USER (required)
      - MYSQL_PASSWORD (required)
      - MYSQL_DB (default: shastho_regulatory)
    """
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DB", "shastho_regulatory"),
        "autocommit": True,
    }

    if overrides:
        config.update(overrides)

    missing = [k for k in ("user", "password") if not config.get(k)]
    if missing:
        raise ValueError(
            f"Missing MySQL configuration for: {', '.join(missing)}. "
            "Set MYSQL_USER and MYSQL_PASSWORD in your environment."
        )

    return mysql.connector.connect(**config)


