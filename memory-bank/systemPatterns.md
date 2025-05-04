# System Patterns

## Application Architecture

### Overall Structure

The shastho application follows a classic Flask application structure with modifications for component-based frontend development:

```
shastho/
  ├── app/                    # Main application package
  │   ├── components/         # Reusable UI components
  │   ├── models/             # Database models
  │   ├── routes/             # API and view routes
  │   ├── services/           # Business logic services
  │   ├── static/             # Static assets (CSS, JS, images)
  │   ├── templates/          # Jinja2 HTML templates
  │   └── utils/              # Utility functions and helpers
  ├── design-system/          # Design system documentation and examples
  ├── frontendExamples/       # Example UI implementations (reference only)
  ├── tasks/                  # Task management files
  ├── app.py                  # Application entry point
  └── requirements.txt        # Python dependencies
```

### Component Based Development

The application uses a component-based approach for frontend development:

1. **Python Components**: Located in `app/components/`, these are Python modules that generate HTML for reusable UI elements (buttons, forms, cards, etc.)
2. **Jinja2 Templates**: Located in `app/templates/`, these extend a base template and use the Python components
3. **Design System**: Documents and demonstrates the components and their usage

This approach allows for consistent UI elements throughout the application while working within the constraints of server-side rendering.

## Design System

The design system is implemented with Tailwind CSS and follows the patterns established in the `frontendExamples/` directory:

1. **Color System**:

   - Primary: Cyan-600 (#0891b2)
   - Primary Hover: Cyan-700 (#0e7490)
   - Primary Light: Cyan-50 (#ecfeff)
   - Success: Green-500 (#10b981)
   - Warning: Amber-500 (#f59e0b)
   - Error: Red-500 (#ef4444)
   - Info: Blue-500 (#3b82f6)

2. **Component Types**:

   - Base components (Button, Input, Card)
   - Composite components (Form, Navbar, Table)
   - Layout components (Container, Grid)

3. **Documentation**:
   - Each component has clear usage examples
   - Design tokens are documented
   - Layout patterns are provided

## Component Implementation

### Python Component Pattern

UI components are implemented as Python functions that generate HTML:

```python
# Example component pattern (Button)
def primary(text, type="button", size="md", full_width=False, icon=None, additional_classes=""):
    """
    Generate HTML for a primary button.
    """
    # Base classes
    classes = "bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors"

    # Size classes
    size_classes = {
        "sm": "px-3 py-1.5 text-sm",
        "md": "px-4 py-2.5",
        "lg": "px-6 py-3 text-lg"
    }

    # Logic to build HTML
    # ...

    return f'<button type="{type}" class="{classes}">{icon_html}{text}</button>'
```

This allows for consistent components with configurable options, while keeping the HTML generation on the server side.

### Template Pattern

Templates follow this structure:

1. **Base Template**: Defines the overall page structure

   ```html
   <!DOCTYPE html>
   <html>
     <head>
       <!-- Meta, CSS, etc. -->
     </head>
     <body>
       <header><!-- Navigation --></header>
       <main>{% block content %}{% endblock %}</main>
       <footer><!-- Footer content --></footer>
     </body>
   </html>
   ```

2. **Page Templates**: Extend the base template

   ```html
   {% extends "base.html" %} {% block content %}
   <!-- Page-specific content -->
   {% endblock %}
   ```

3. **Component Usage**: Components are used within routes

   ```python
   from app.components import button

   @app.route('/example')
   def example():
       primary_btn = button.primary("Click Me")
       return render_template('example.html', primary_btn=primary_btn)
   ```

## Database Schema (Planned)

The database schema will be implemented in Supabase (PostgreSQL) with the following key tables:

1. **Users**: Core user information and authentication
2. **Roles**: User roles (Patient, Doctor, Hospital Admin, etc.)
3. **Hospitals**: Hospital information
4. **Departments**: Hospital departments
5. **Doctors**: Doctor profiles and specialties
6. **Appointments**: Appointment scheduling
7. **EHR**: Electronic health records
8. **Prescriptions**: Medication prescriptions
9. **Tests**: Medical test requests and results
10. **Feedback**: User feedback and ratings

## Authentication Flow (Planned)

The authentication system will be a simple database-based approach:

1. **Registration**:

   - Role-specific registration forms
   - Email verification
   - Initial password setup

2. **Login**:

   - Email/password authentication
   - Role-based redirection after login
   - Session management

3. **Authorization**:
   - Role-based access control
   - Permission checks in routes and templates

## Routing Structure (Implemented)

Routes are organized by feature and implemented using Flask Blueprints:

```python
# Main blueprint example
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page route"""
    return render_template('index.html', title='Home')
```

Blueprints are registered in the main app:

```python
# In app.py
def create_app():
    app = Flask(__name__,
               template_folder='app/templates',
               static_folder='app/static')

    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
```

## Database Connection (Implemented)

Supabase client is implemented as a utility function:

```python
# In app/utils/db.py
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

def get_supabase_client():
    """
    Create and return a Supabase client instance.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and key must be provided in environment variables")

    return create_client(supabase_url, supabase_key)
```

## Environment Configuration (Implemented)

Environment variables are loaded from a `.env` file and include:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
DATABASE_URL=your_database_url_here
```

## Testing Strategy (Planned)

Testing will be implemented with pytest:

1. **Unit Tests**: For individual components and functions
2. **Integration Tests**: For API endpoints and database interactions
3. **Functional Tests**: For end-to-end user flows

## Deployment Strategy (Planned)

The application will be deployed using:

1. **Web Server**: Gunicorn (included in requirements.txt)
2. **Database**: Supabase (PostgreSQL)
3. **Static Assets**: Served directly through Flask in initial deployment
