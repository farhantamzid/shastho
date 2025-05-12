"""
Flask Application Initialization
-------------------------------
This is the main entry point for the Shastho healthcare platform Flask application.
This file is responsible for:
1. Creating and configuring the Flask application
2. Initializing all required extensions (Session, LoginManager, CSRF)
3. Setting up localization
4. Registering all blueprints for different user roles
5. Establishing user session management
6. Setting up the user loading mechanism for authentication

The file creates a factory function pattern where the application instance
is created and configured dynamically, which facilitates easier testing
and multiple instance creation if necessary.
"""

import os
from flask import Flask, request, session
from flask_session import Session as FlaskSessionExt
from flask_login import LoginManager
from datetime import timedelta
from dotenv import load_dotenv
from app.utils.localization import setup_localization
from flask_wtf.csrf import CSRFProtect
from app.config import Config

# Initialize extensions using the renamed import to avoid naming conflicts
# with the Flask session object
session_ext = FlaskSessionExt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Specify the login route for unauthorized access
login_manager.login_message_category = 'info'  # Bootstrap message category for login messages

# Main application factory function
# This function is called to create and configure the Flask app instance
# It sets up all extensions, blueprints, and global context

def create_app(config_class=Config):
    """Create and configure the Flask app.

    Args:
        config_class: Configuration class to use (default: app.config.Config)

    Returns:
        A configured Flask application instance
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create the Flask application instance
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Configure the app with settings from config class
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    session_ext.init_app(app)  # Server-side session management
    login_manager.init_app(app)  # User authentication management

    # Initialize CSRF protection for form security
    csrf = CSRFProtect(app)

    # Set up localization for multi-language support
    setup_localization(app)

    # Register blueprints for different application modules
    # Each blueprint handles a specific part of the application
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.doctor import doctor_bp
    from app.routes.patient import patient_bp
    from app.routes.hospital_admin import hospital_admin_bp
    from app.routes.api import api_bp
    from app.routes.regulatory_body import regulatory_body_bp

    # Register each blueprint with the app, some with URL prefixes
    app.register_blueprint(main_bp)  # Main routes at root URL
    app.register_blueprint(auth_bp)  # Authentication routes at root URL
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Admin routes prefixed with /admin
    app.register_blueprint(doctor_bp, url_prefix='/doctor')  # Doctor routes prefixed with /doctor
    app.register_blueprint(patient_bp, url_prefix='/patient')  # Patient routes prefixed with /patient
    app.register_blueprint(hospital_admin_bp, url_prefix='/hospital-admin')  # Hospital admin routes
    app.register_blueprint(api_bp, url_prefix='/api')  # API routes prefixed with /api
    app.register_blueprint(regulatory_body_bp, url_prefix='/regulatory')  # Regulatory body routes

    # Setup Jinja environment with global template variables
    @app.context_processor
    def inject_constants():
        """Inject constants into Jinja templates.

        Returns:
            Dictionary of constants available in all templates
        """
        return dict(
            APP_NAME="Shastho",
            APP_VERSION="1.0.0",
        )

    # Configure session before each request
    @app.before_request
    def make_session_permanent():
        """Set session timeout to 24 hours."""
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)

    # Load the user for the login manager
    from app.models.auth import User, find_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        """Load a user by ID for Flask-Login.

        Args:
            user_id: ID of the user to load (string)

        Returns:
            A User object or None if not found
        """
        return find_user_by_id(user_id)  # Find user from database by ID

    return app  # Return the configured application instance