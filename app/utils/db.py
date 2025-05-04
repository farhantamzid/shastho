import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

def get_supabase_client():
    """
    Create and return a Supabase client instance.

    Returns:
        supabase.Client: A configured Supabase client
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and key must be provided in environment variables")

    return create_client(supabase_url, supabase_key)