# Main application package

import os
from flask import Flask, request, session
from flask_session import Session as FlaskSessionExt
from flask_login import LoginManager
from datetime import timedelta
from dotenv import load_dotenv
from app.utils.localization import setup_localization
from flask_wtf.csrf import CSRFProtect
from app.config import Config

# Initialize extensions using the renamed import
session_ext = FlaskSessionExt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    """Create and configure the Flask app."""
    # Load environment variables
    load_dotenv()

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Configure the app
    app.config.from_object(config_class)

    # Initialize extensions with app using the renamed variable
    session_ext.init_app(app)
    login_manager.init_app(app)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Set up localization
    setup_localization(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.doctor import doctor_bp
    from app.routes.patient import patient_bp
    from app.routes.hospital_admin import hospital_admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(hospital_admin_bp, url_prefix='/hospital-admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Setup Jinja environment
    @app.context_processor
    def inject_constants():
        """Inject constants into Jinja templates."""
        return dict(
            APP_NAME="Shastho",
            APP_VERSION="1.0.0",
        )

    # Configure session
    @app.before_request
    def make_session_permanent():
        """Set session timeout."""
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)

    # This is typically where your user loader function would be defined
    # For example, if your User model is in app.models.auth
    from app.models.auth import User, find_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        # Replace this with your actual user loading logic
        # This function should take a user_id (string) and return a user object, or None
        return find_user_by_id(user_id) # Assuming find_user_by_id returns a User object

    return app