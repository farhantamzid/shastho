# Main application package

import os
from flask import Flask
from flask_session import Session
from datetime import timedelta
from dotenv import load_dotenv
from app.utils.localization import setup_localization

def create_app():
    """Create and configure the Flask application."""
    # Load environment variables
    load_dotenv()

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Configure the app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-development')

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'shastho_'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')

    # Initialize Flask-Session
    Session(app)

    # Set up localization
    setup_localization(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.hospital_admin import hospital_admin_bp
    from app.routes.doctor import doctor_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(hospital_admin_bp)
    app.register_blueprint(doctor_bp)

    return app