from flask import request, session, g, current_app
import os
import json
from functools import lru_cache

# Dictionary to store translations
_translations = {}

@lru_cache(maxsize=128)
def get_translation(key, language='english'):
    """Get translation for a key in the specified language."""
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
    """Load all translation files."""
    translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'translations')

    # Create translations directory if it doesn't exist
    os.makedirs(translations_dir, exist_ok=True)

    # Look for translation files
    for filename in os.listdir(translations_dir):
        if filename.endswith('.json'):
            language = filename.rsplit('.', 1)[0]
            with open(os.path.join(translations_dir, filename), 'r', encoding='utf-8') as f:
                try:
                    _translations[language] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error loading translation file: {filename}")

def get_user_language():
    """Get the current user's language preference."""
    return session.get('language', 'english')

def setup_localization(app):
    """Set up localization for the application."""
    # Load translations
    load_translations()

    # Create translations directory and example files if they don't exist
    create_example_translation_files()

    # Register template function
    @app.template_filter('t')
    def translate_filter(text):
        return get_translation(text, get_user_language())

    # Before request handler to set language
    @app.before_request
    def set_user_language():
        g.language = get_user_language()
        g.translate = lambda text: get_translation(text, g.language)

def create_example_translation_files():
    """Create example translation files if they don't exist."""
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