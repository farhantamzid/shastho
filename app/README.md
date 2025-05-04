# shastho Flask Application

## Project Overview

shastho is a healthcare platform built with Flask, Tailwind CSS, and Supabase. The application provides electronic health records, appointment scheduling, and doctor search functionality.

## Setting Up the Development Environment

### Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the repository (if not already done)**

   ```bash
   git clone <repository-url>
   cd shastho
   ```

2. **Set up a Python virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Create a `.env` file in the root directory
   - Add the following variables:
     ```
     FLASK_APP=app.py
     FLASK_ENV=development
     SECRET_KEY=your_secret_key_here
     SUPABASE_URL=your_supabase_url_here
     SUPABASE_KEY=your_supabase_anon_key_here
     DATABASE_URL=your_database_url_here
     ```

## Running the Application

1. **Start the Flask development server**

   ```bash
   python app.py
   ```

2. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:5000/`

## Project Structure

```
/app
  /components - Reusable UI components
  /models - Database models
  /routes - API routes
  /services - Business logic
  /static - Static files (CSS, JS)
  /templates - HTML templates
  /utils - Utility functions
app.py - Main application entry point
requirements.txt - Python dependencies
```

## Design System

The application follows the design system conventions established in the `design-system` directory.
See `design-system/README.md` for more information on available components and design patterns.

## Development Guidelines

- Follow the established design patterns from `frontendExamples/` and `design-system/`
- Use the Supabase client for database operations
- Organize components and templates according to the project structure
- Maintain responsive design principles from the design tokens

## Testing

Run tests with pytest:

```bash
python -m pytest
```
