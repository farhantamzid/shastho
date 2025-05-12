"""
API routes for the Shastho Flask application.
--------------------------------------------
This file defines lightweight API endpoints for AJAX or external integrations.
Each route is registered as part of the 'api_bp' blueprint in app/__init__.py.
"""
from flask import Blueprint, jsonify, request
from app.utils.auth import login_required, role_required # Or specific API key auth
from app.models.database import UserRole
from app.utils.db import Database

api_bp = Blueprint('api', __name__, url_prefix='/api')
db = Database()

# Placeholder API route
@api_bp.route('/status')
def api_status():
    return jsonify({'status': 'ok', 'message': 'API is running'})

# Add other API endpoints here (e.g., for fetching data, integrations)