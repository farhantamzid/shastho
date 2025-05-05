import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    # Add other configuration variables as needed
    # Example: SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_TYPE = 'filesystem' # Example: Can be redis, memcached, sqlalchemy etc.
    SESSION_FILE_DIR = '../flask_session' # Directory to store session files
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'session:'