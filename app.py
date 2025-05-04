import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')

    # Configure the app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-development')

    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)