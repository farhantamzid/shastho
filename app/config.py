"""
Configuration file for the Shastho Flask application.
---------------------------------------------------
This file defines the Config class, which holds all configuration settings for the app.
These settings include secret keys, database URIs, session configs, and other Flask extensions.
The config is loaded in app/__init__.py to configure the Flask app instance.

It uses python-dotenv to load environment variables from a .env file
and provides fallback values when environment variables are not set.

Configuration parameters include:
- Secret key for secure sessions and CSRF protection
- Supabase credentials for database access
- Session configuration settings
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    """Application configuration settings.

    This class contains all the configuration settings for the application.
    Settings can be overridden by environment variables.
    """

    # Secret key used for session signing and CSRF protection
    # Should be set in environment variables for production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Supabase connection credentials
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    # Add other configuration variables as needed
    # Example: SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Session configuration
    SESSION_TYPE = 'filesystem'  # Session storage backend (filesystem, redis, memcached, etc.)
    SESSION_FILE_DIR = '../flask_session'  # Directory to store session files
    SESSION_PERMANENT = False  # Session expires when the browser is closed
    SESSION_USE_SIGNER = True  # Sign session cookie for extra security
    SESSION_KEY_PREFIX = 'session:'  # Prefix for session keys in storage