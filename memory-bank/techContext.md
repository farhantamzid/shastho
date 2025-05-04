# Technical Context

## Technology Stack

### Backend

- **Python 3.12**: Core programming language for backend development
- **Flask 2.3.3**: Lightweight web framework for building the application
- **Jinja2 3.1.2**: Templating engine for server-side HTML rendering
- **Werkzeug 2.3.7**: WSGI utility library used by Flask
- **Gunicorn 21.2.0**: WSGI HTTP Server for deployment

### Database

- **PostgreSQL**: Relational database via Supabase
- **Supabase 1.2.0**: Backend-as-a-Service for database management
- **psycopg2-binary 2.9.9**: PostgreSQL adapter for Python

### Frontend

- **HTML5**: Standard markup language for web pages
- **Tailwind CSS**: Utility-first CSS framework for styling
- **JavaScript**: Minimal usage for enhanced interactivity

### Development Tools

- **python-dotenv 1.0.0**: Environment variable management
- **pytest 7.4.2**: Testing framework for Python
- **Flask-WTF 1.2.1**: Form handling and validation for Flask

## Project Structure

The project follows a modular Flask application structure:

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
  ├── design-system/          # Design system documentation
  ├── frontendExamples/       # Example UI implementations (reference)
  ├── app.py                  # Application entry point
  └── requirements.txt        # Python dependencies
```

## Development Environment Setup

### Local Development

1. **Python Environment**:

   - Python 3.12+ required
   - Virtual environment using `venv` module

2. **Dependencies**:

   - Installed via `pip install -r requirements.txt`

3. **Environment Variables**:

   - Stored in `.env` file (not version controlled)
   - Required variables:
     ```
     FLASK_APP=app.py
     FLASK_ENV=development
     SECRET_KEY=your_secret_key_here
     SUPABASE_URL=your_supabase_url_here
     SUPABASE_KEY=your_supabase_anon_key_here
     DATABASE_URL=your_database_url_here
     ```

4. **Running Locally**:
   - Activate virtual environment
   - Run `python app.py`
   - Access at http://127.0.0.1:5000/

### Version Control

- **Git**: Source code versioning
- **Repository Structure**:
  - Main branch for stable releases
  - Development branch for ongoing work
  - Feature branches for new functionality

## Key Technical Implementations

### Flask Application Setup

The application is initialized in `app.py`:

```python
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
```

### Component-Based UI Development

UI components are implemented as Python functions that generate HTML:

```python
# app/components/button.py
def primary(text, type="button", size="md", full_width=False, icon=None, additional_classes=""):
    """Generate HTML for a primary button."""
    classes = "bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors"

    # Size classes
    size_classes = {
        "sm": "px-3 py-1.5 text-sm",
        "md": "px-4 py-2.5",
        "lg": "px-6 py-3 text-lg"
    }

    classes += f" {size_classes.get(size, size_classes['md'])}"

    # Width class
    if full_width:
        classes += " w-full"

    # Add any additional classes
    if additional_classes:
        classes += f" {additional_classes}"

    # Add icon if provided
    icon_html = f"{icon} " if icon else ""

    return f'<button type="{type}" class="{classes}">{icon_html}{text}</button>'
```

### Tailwind CSS Integration

Tailwind CSS is integrated via CDN in development and configured with design tokens:

```html
<!-- In app/templates/base.html -->
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          primary: "#0891b2" /* cyan-600 */,
          "primary-hover": "#0e7490" /* cyan-700 */,
          "primary-light": "#ecfeff" /* cyan-50 */,
          success: "#10b981" /* green-500 */,
          warning: "#f59e0b" /* amber-500 */,
          error: "#ef4444" /* red-500 */,
          info: "#3b82f6" /* blue-500 */,
        },
      },
    },
  };
</script>
```

### Supabase Integration

Supabase is integrated as the database backend:

```python
# app/utils/db.py
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

def get_supabase_client():
    """Create and return a Supabase client instance."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and key must be provided in environment variables")

    return create_client(supabase_url, supabase_key)
```

## Database Structure (Planned)

The database will be implemented in Supabase with the following key tables:

1. **users**

   - id (primary key)
   - email
   - password_hash
   - role
   - created_at
   - last_login

2. **patients**

   - id (primary key)
   - user_id (foreign key)
   - name
   - gender
   - date_of_birth
   - contact_info
   - address

3. **doctors**
   - id (primary key)
   - user_id (foreign key)
   - name
   - specialization
   - license_number
   - hospital_id (foreign key)
   - department_id (foreign key)
   - bio
   - status (pending, active, suspended)

Additional tables will be designed for hospitals, departments, appointments, EHR data, etc.

## Authentication (Planned)

A database-based authentication system will be implemented with features:

1. **Registration**

   - User information collection
   - Password hashing
   - Role assignment

2. **Login**

   - Credential verification
   - Session creation
   - Role-based redirection

3. **Authorization**
   - Role-based access control
   - Permission checks
   - Secure routes

## Testing Approach (Planned)

Testing will be implemented with pytest:

1. **Unit Tests**

   - Component functions
   - Utility functions
   - Service methods

2. **Integration Tests**

   - API endpoints
   - Database interactions
   - Form submissions

3. **Functional Tests**
   - End-to-end user flows
   - UI interactions

## Deployment (Planned)

The application will be deployed using:

1. **Application Server**: Gunicorn
2. **Database**: Supabase (PostgreSQL)
3. **Static Assets**: Initially served through Flask

## Technical Constraints

The development adheres to the following constraints:

1. **Simplicity First**: Avoid unnecessary complexity
2. **Minimal JavaScript**: Server-side rendering is preferred
3. **Mobile Responsiveness**: All pages must work on mobile devices
4. **Accessibility**: Must meet WCAG guidelines
5. **Performance**: Fast page loads and minimal resource usage
