"""
Localization setup for the Shastho Flask application.
----------------------------------------------------
This file contains functions to set up and manage multi-language support for the app.
Called during app initialization to enable translations.

Localization Utility Module
--------------------------
This module provides internationalization/localization functionality for the application.
It manages translations of UI text into different languages based on user preferences.

Features:
- Loading translations from JSON files
- Retrieving translations based on keys and language settings
- Setting user language preferences
- Creating example translation files
- Integrating with Flask templates through filters

This implementation uses JSON files stored in the static/translations directory
rather than more complex solutions like gettext to maintain simplicity
while still providing multilingual support.
"""

from flask import request, session, g, current_app
import os
import json
from functools import lru_cache

# Dictionary to store translations loaded from JSON files
_translations = {}

@lru_cache(maxsize=128)
def get_translation(key, language='english'):
    """Get translation for a key in the specified language.

    Uses LRU cache to improve performance by caching frequently used translations.
    Falls back to English if the requested translation is not available.

    Args:
        key: The text key to translate
        language: The target language code (default: 'english')

    Returns:
        Translated text if available, otherwise returns the key itself
    """
    # If translations not loaded, load them
    if not _translations:
        load_translations()

    # Get translation or return key if not found
    if language in _translations and key in _translations[language]:
        return _translations[language][key]
    elif 'english' in _translations and key in _translations['english']:
        return _translations['english'][key]  # Fallback to English
    else:
        return key  # Return the key itself if no translation found

def load_translations():
    """Load all translation files from the translations directory.

    Scans the translations directory for JSON files and loads each one
    into the _translations dictionary. The filename (minus extension)
    is used as the language code.
    """
    translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'translations')

    # Create translations directory if it doesn't exist
    os.makedirs(translations_dir, exist_ok=True)

    # Look for translation files
    for filename in os.listdir(translations_dir):
        if filename.endswith('.json'):
            language = filename.rsplit('.', 1)[0]  # Extract language name from filename
            with open(os.path.join(translations_dir, filename), 'r', encoding='utf-8') as f:
                try:
                    _translations[language] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error loading translation file: {filename}")

def get_user_language():
    """Get the current user's language preference.

    Retrieves the language preference from the session,
    defaulting to English if not set.

    Returns:
        String language code (e.g., 'english', 'bangla')
    """
    return session.get('language', 'english')

def setup_localization(app):
    """Set up localization for the application.

    This function initializes the localization system and integrates it
    with the Flask application:
    1. Loads all available translations
    2. Creates example translation files if none exist
    3. Registers a template filter for easy translation in templates
    4. Sets up a before_request handler to make translation available in requests

    Args:
        app: The Flask application instance
    """
    # Load translations
    load_translations()

    # Create translations directory and example files if they don't exist
    create_example_translation_files()

    # Register template filter 't' for use in templates like {{ 'Hello'|t }}
    @app.template_filter('t')
    def translate_filter(text):
        """Template filter for translating text in templates.

        Usage in templates: {{ 'Hello'|t }}

        Args:
            text: The text key to translate

        Returns:
            Translated text based on current user language
        """
        return get_translation(text, get_user_language())

    # Before request handler to set language and translation function
    @app.before_request
    def set_user_language():
        """Sets language and translation function for each request.

        Makes the current language and a translation function available
        in the g object for access in route handlers.
        """
        g.language = get_user_language()
        g.translate = lambda text: get_translation(text, g.language)

def create_example_translation_files():
    """Create example translation files if they don't exist.

    This function ensures that there are at least basic translation files
    available for English and Bangla when the application first runs.
    These example files provide a template for adding more translations.
    """
    translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'translations')
    os.makedirs(translations_dir, exist_ok=True)

    # Example English translations
    english_file = os.path.join(translations_dir, 'english.json')
    if not os.path.exists(english_file):
        examples = {
            "Welcome": "Welcome",
            "Login": "Login",
            "Register": "Register",
            "Dashboard": "Dashboard",
            "Profile": "Profile",
            "Settings": "Settings",
            "Logout": "Logout",
            "Home": "Home",
            "Services": "Services",
            "Doctors": "Doctors",
            "About": "About",
            "Contact": "Contact"
        }
        with open(english_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)

    # Example Bangla translations
    bangla_file = os.path.join(translations_dir, 'bangla.json')
    if not os.path.exists(bangla_file):
        examples = {
            "Welcome": "স্বাগতম",
            "Login": "লগইন",
            "Register": "নিবন্ধন",
            "Dashboard": "ড্যাশবোর্ড",
            "Profile": "প্রোফাইল",
            "Settings": "সেটিংস",
            "Logout": "লগআউট",
            "Home": "হোম",
            "Services": "সেবাসমূহ",
            "Doctors": "ডাক্তারবৃন্দ",
            "About": "সম্পর্কে",
            "Contact": "যোগাযোগ"
        }
        with open(bangla_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)