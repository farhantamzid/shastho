import os
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import timedelta
from flask_session import Session

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')

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

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)