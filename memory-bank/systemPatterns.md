# System Patterns

## Architecture Overview

Shastho follows a classic MVC (Model-View-Controller) architecture with Flask:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Web Browser)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     Flask Application                        │
│                                                             │
│  ┌───────────────┐     ┌───────────────┐    ┌────────────┐  │
│  │   Routes &    │     │   Services &  │    │   Models   │  │
│  │  Controllers  │◄───►│   Business    │◄──►│            │  │
│  │               │     │     Logic     │    │            │  │
│  └───────────────┘     └───────────────┘    └────────────┘  │
│         │                                      │           │
│         ▼                                      │           │
│  ┌───────────────┐                             │           │
│  │  Design System│                             │           │
│  │   Components  │                             │           │
│  └───────────────┘                             │           │
│                                                │           │
└────────────────────────────────────────────────┼───────────┘
                                                 │
┌────────────────────────────────────────────────▼───────────┐
│                       Supabase                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                PostgreSQL Database                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Repository Pattern

Database interactions are abstracted through repository classes to separate data access from business logic:

```python
class UserRepository:
    def get_by_id(self, user_id):
        # Database query logic

    def create(self, user_data):
        # Insert logic
```

### 2. Service Layer Pattern

Business logic is encapsulated in service classes:

```python
class AppointmentService:
    def __init__(self, appointment_repo, doctor_repo):
        self.appointment_repo = appointment_repo
        self.doctor_repo = doctor_repo

    def book_appointment(self, patient_id, doctor_id, time_slot):
        # Check availability, validate, and book
```

### 3. Blueprint Pattern (Flask)

The application is organized into logical modules using Flask Blueprints:

```python
# auth_blueprint.py
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic

# In app.py
app.register_blueprint(auth_bp, url_prefix='/auth')
```

### 4. Design System Component Pattern

For frontend components, we've established a comprehensive design system with a consistent component architecture pattern:

```javascript
/**
 * ComponentName Component
 *
 * Brief description of what it does.
 *
 * Usage examples in JSDoc comments.
 */
class ComponentName {
  constructor() {
    // Base classes and default configuration
    this.baseClasses = "...";
  }

  /**
   * Renders the component with options
   * @param {Object} options - Component options
   * @returns {string} HTML markup
   */
  render(options = {}) {
    // Combine classes, process options
    return `<!-- Generated HTML -->`;
  }

  // Helper methods for common variants
  variantName(options = {}) {
    return this.render({ variant: "name", ...options });
  }
}

export default new ComponentName();
```

This pattern allows for consistent rendering, composition, and styling across the UI.

## Design System Architecture

Our UI Design System follows a modular architecture with clear hierarchy and composition patterns:

### 1. Design Tokens

Foundational visual attributes with standardized values:

- **Colors**: Primary (cyan), neutrals, semantic (success, warning, error)
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Consistent spacing scale (aligned with Tailwind defaults)
- **Borders & Radii**: Border widths, styles, and border radius values
- **Shadows**: Elevation levels and shadow definitions
- **Breakpoints**: Responsive design breakpoints (sm, md, lg, xl)
- **Z-Index**: Stacking order scale

### 2. Base UI Components

Atomic, single-purpose UI elements:

- **Button**: Multiple variants (primary, secondary, outline, link) with consistent states
- **Input**: Text, email, password inputs with validation states
- **Select**: Dropdown selection components
- **Checkbox**: Selection controls
- **Alert**: System messaging (success, warning, error, info)
- **Card**: Content containers with various configurations

### 3. Composite Components

UI elements composed of multiple base components:

- **Form**: Component composition with section support
- **Navbar**: Site navigation with responsive behavior
- **Sidebar**: Secondary navigation for dashboard layouts
- **Table**: Data display with various styling options

### 4. Layout Components

Structural components for page organization:

- **PageLayout**: Page structure templates (default, dashboard, auth)
- **Container**: Width constraints with responsive behavior
- **Grid**: Responsive grid system for columnar layouts

### 5. Layout Patterns

Standardized page structures for common scenarios:

- **Dashboard Layout**: Admin interfaces with sidebar navigation
- **Authentication Layout**: Login/registration pages
- **Content Layout**: General content pages

## Data Flow Patterns

### Authentication Flow

1. User submits login credentials
2. Flask route handler validates input
3. Authentication service verifies credentials against database
4. Session is created upon successful authentication
5. User is redirected based on role

### Appointment Booking Flow

1. Patient selects hospital → department → doctor → time slot
2. System validates slot availability
3. Appointment is created in database
4. Confirmation is shown to patient

### EHR Access Control Flow

1. Doctor/patient requests EHR data
2. Authorization middleware checks user role and permissions
3. If authorized, EHR service retrieves data
4. Data is filtered based on user role before being returned

## Persistent Data Models

Core data models and their relationships:

```
Users ─┬─ Patients
       ├─ Doctors ─┬─ DoctorAvailability
       │           └─ Departments
       ├─ HospitalAdmins
       ├─ SystemAdmins
       ├─ TestAdmins
       └─ GovtUsers

Hospitals ─┬─ Departments
           └─ Feedback

Appointments ─┬─ Patients
              ├─ Doctors
              └─ Departments

EHR ─┬─ Patients
     ├─ Visits
     ├─ Diagnoses
     ├─ Medications
     ├─ TestResults
     └─ ProviderNotes
```

This architecture supports modularity, maintainability, and the phased development approach outlined in the PRD.
