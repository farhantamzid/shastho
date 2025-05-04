# Technical Context

## Technology Stack

### Backend

- **Primary Framework**: Python Flask
- **API Structure**: RESTful API endpoints
- **Authentication**: Database-based authentication (not using Supabase Auth)
- **Business Logic**: Object-Oriented Python

### Frontend

- **HTML/CSS**: Semantic HTML5 with Tailwind CSS
- **JavaScript**: Minimal vanilla JavaScript for interactivity
- **Design System**: Comprehensive component library based on frontendExamples/
- **UI Framework**: None (no React, Vue, Angular, etc.)

### Database

- **Database System**: PostgreSQL (managed via Supabase)
- **ORM/Access**: Direct SQL via supabase-py or psycopg2
- **Schema Management**: Manual migrations

### Infrastructure

- **Hosting**: Web hosting for Flask application (specific provider TBD)
- **Database Hosting**: Supabase for PostgreSQL
- **File Storage**: Local file system (initial implementation)

## Development Environment

### Required Tools

- **Python**: 3.8+ with pip
- **Node.js**: For Tailwind CSS compilation
- **Git**: Version control
- **Virtual Environment**: venv or similar for Python dependency isolation

### Key Dependencies

- **Flask**: Web framework
- **psycopg2-binary**: PostgreSQL adapter
- **supabase-py**: Python client for Supabase
- **python-dotenv**: Environment variable management
- **Tailwind CSS**: Utility-first CSS framework
- **PyTest**: Testing framework

## Design System Architecture

### Component Organization

```
design-system/
├── components/
│   ├── buttons/
│   │   └── Button.js
│   ├── forms/
│   │   ├── Input.js
│   │   ├── Select.js
│   │   ├── Checkbox.js
│   │   └── Form.js
│   ├── layouts/
│   │   ├── Container.js
│   │   ├── Grid.js
│   │   └── PageLayout.js
│   ├── navigation/
│   │   ├── Navbar.js
│   │   └── Sidebar.js
│   ├── Alert.js
│   ├── Card.js
│   └── Table.js
└── docs/
    ├── design-tokens.md
    ├── layout-patterns.md
    └── coding-standards.md
```

### Component Implementation Pattern

The design system uses a consistent class-based component pattern:

```javascript
class ComponentName {
  constructor() {
    // Define base classes and defaults
    this.baseClasses = "...";
  }

  // Main render method with options
  render(options = {}) {
    // Component logic & HTML generation
    return `<div class="...">...</div>`;
  }

  // Helper methods for variants
  variantName(options = {}) {
    return this.render({ variant: "variant", ...options });
  }
}

export default new ComponentName();
```

### Design Tokens

Standardized design values documented in `design-tokens.md`:

- Color palette: Primary (cyan-600), neutrals, semantic colors
- Typography: Font families, sizes, weights, line heights
- Spacing: Standardized spacing scale
- Borders, shadows, and other visual attributes

### CSS Approach

- Uses Tailwind CSS utility classes
- Follows mobile-first responsive design
- Consistent class composition pattern
- No custom CSS (using only Tailwind utilities)

## Integration Points

### Supabase Integration

- PostgreSQL database access
- No direct use of Supabase Auth, Storage, or Functions
- Using Python API client for database operations

### External APIs

- None for MVP (no NID, SMS, Email, AI/LLM APIs)

## Security Considerations

- **Authentication**: Password hashing with bcrypt
- **Session Management**: Server-side sessions with Flask-Session
- **Access Control**: Role-based access control (RBAC)
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: CSRF tokens for forms

## Monitoring & Logging

- **Application Logs**: Python logging module
- **Error Tracking**: Custom error pages and logging
- **Performance Monitoring**: TBD for production

## Deployment Strategy

- **Development**: Local development environment
- **Staging**: TBD
- **Production**: Web hosting for Flask + Supabase for database

## Technical Constraints

1. **Simplicity**: Minimize technical complexity and external dependencies
2. **Performance**: Optimize for Bangladesh's internet conditions
3. **Internationalization**: Support for Bangla and English
4. **Accessibility**: WCAG compliance (implemented in design system components)
5. **Responsive Design**: Support for all device sizes (built into design system)
6. **Offline Capability**: Not required for MVP

This technical approach prioritizes straightforward implementation, maintainability, and alignment with the phased development approach outlined in the PRD.
