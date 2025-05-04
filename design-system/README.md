# HealthBD Design System

A comprehensive design system for the HealthBD application, providing consistent UI components, design tokens, and guidelines for frontend development.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Design Tokens](#design-tokens)
- [Components](#components)
- [Layout Patterns](#layout-patterns)
- [Coding Standards](#coding-standards)
- [Usage Examples](#usage-examples)

## Overview

The HealthBD Design System is a collection of reusable components, design tokens, and patterns that ensure consistency across the application. It serves as a single source of truth for the UI implementation, helping developers build interfaces that are visually consistent, accessible, and performant.

### Key Benefits

- **Consistency**: Provides a unified look and feel across all parts of the application
- **Efficiency**: Speeds up development by providing ready-to-use components
- **Maintainability**: Centralizes UI code to make updates and changes easier
- **Accessibility**: Ensures components meet accessibility standards
- **Scalability**: Makes it easier to extend the UI as the application grows

## Getting Started

To use the design system in your project:

1. Import the components you need:

   ```javascript
   import Button from "../design-system/components/buttons/Button";
   import Input from "../design-system/components/forms/Input";
   ```

2. Use the components in your HTML:

   ```javascript
   const loginForm = `
     <div>
       ${Input.text({ name: "email", label: "Email Address", required: true })}
       ${Input.password({
         name: "password",
         label: "Password",
         required: true,
       })}
       ${Button.primary({ text: "Sign In", type: "submit", fullWidth: true })}
     </div>
   `;
   ```

3. Refer to the documentation and usage examples for each component.

## Design Tokens

Design tokens are the visual design atoms of the design system — specifically, they are named entities that store visual design attributes. We use them in place of hard-coded values to ensure a scalable and consistent visual system.

- [Color Palette](./design-tokens.md#color-palette)
- [Typography](./design-tokens.md#typography)
- [Spacing](./design-tokens.md#spacing)
- [Borders & Rounded Corners](./design-tokens.md#borders--rounded-corners)
- [Shadows](./design-tokens.md#shadows)
- [Responsive Breakpoints](./design-tokens.md#responsive-breakpoints)
- [Z-Index Scale](./design-tokens.md#z-index-scale)

For full details, see the [Design Tokens documentation](./design-tokens.md).

## Components

The design system includes the following component categories:

### Basic UI Components

- **Buttons**: [/components/buttons/Button.js](./components/buttons/Button.js)
  - Primary, secondary, outline, and link variants
  - Multiple sizes
  - Icon support
- **Forms**:

  - [Input](./components/forms/Input.js): Text inputs, password fields, etc.
  - [Select](./components/forms/Select.js): Dropdown selectors
  - [Checkbox](./components/forms/Checkbox.js): Checkboxes and checkbox groups
  - [Form](./components/forms/Form.js): Form layouts and validation

- **Alert**: [Alert.js](./components/Alert.js)

  - Success, error, warning, and info variants
  - Dismissible option

- **Card**: [Card.js](./components/Card.js)

  - Standard, interactive, and borderless variants
  - Header/content/footer structure

- **Table**: [Table.js](./components/Table.js)
  - Responsive tables
  - Striped, hoverable, and bordered variants

### Navigation Components

- **Navbar**: [Navbar.js](./components/navigation/Navbar.js)

  - Responsive navigation bar
  - Support for dropdown menus

- **Sidebar**: [Sidebar.js](./components/navigation/Sidebar.js)
  - Collapsible sidebar navigation
  - Mobile and desktop variants

### Layout Components

- **Container**: [Container.js](./components/layouts/Container.js)

  - Content containment with consistent max-widths
  - Multiple size variants

- **Grid**: [Grid.js](./components/layouts/Grid.js)

  - Responsive grid layouts
  - Custom column configurations

- **PageLayout**: [PageLayout.js](./components/layouts/PageLayout.js)
  - Page layout templates
  - Dashboard, authentication, and standard layouts

## Layout Patterns

The design system includes standard layout patterns for common page types:

- [Dashboard Layout](./docs/layout-patterns.md#dashboard-page-pattern)
- [Authentication Layout](./docs/layout-patterns.md#authentication-page-pattern)
- [Content Layout](./docs/layout-patterns.md#content-page-pattern)
- [Responsive Behavior](./docs/layout-patterns.md#responsive-behavior)

For full details, see the [Layout Patterns documentation](./docs/layout-patterns.md).

## Coding Standards

To maintain consistency and quality in the codebase, we follow a set of coding standards:

- [Component Structure](./docs/coding-standards.md#component-structure)
- [Naming Conventions](./docs/coding-standards.md#naming-conventions)
- [Documentation Standards](./docs/coding-standards.md#documentation-standards)
- [CSS/Tailwind Patterns](./docs/coding-standards.md#csstailwind-patterns)
- [Accessibility Standards](./docs/coding-standards.md#accessibility-standards)
- [Performance Considerations](./docs/coding-standards.md#performance-considerations)

For full details, see the [Coding Standards documentation](./docs/coding-standards.md).

## Usage Examples

### Basic Page with Navbar and Content

```javascript
// Import components
import Navbar from "./components/navigation/Navbar";
import Container from "./components/layouts/Container";
import PageLayout from "./components/layouts/PageLayout";
import Button from "./components/buttons/Button";

// Create navbar
const navbar = Navbar.render({
  logo: '<img src="/logo.svg" alt="HealthBD" class="h-8 w-auto">',
  items: [
    { text: "Home", href: "/", active: true },
    { text: "Services", href: "/services" },
    { text: "About", href: "/about" },
    { text: "Contact", href: "/contact" },
  ],
});

// Create page content
const content = Container.render({
  content: `
    <div class="py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Welcome to HealthBD</h1>
      <p class="text-lg text-gray-700 mb-6">Your comprehensive healthcare solution.</p>
      ${Button.primary({ text: "Get Started", size: "lg" })}
    </div>
  `,
});

// Render the complete page
const page = PageLayout.render({
  header: navbar,
  content: content,
  footer:
    '<footer class="bg-gray-50 border-t py-6 text-center text-gray-600">© 2023 HealthBD. All rights reserved.</footer>',
});

// Output the page HTML
document.getElementById("app").innerHTML = page;
```

### Dashboard Layout

```javascript
// Import components
import Navbar from "./components/navigation/Navbar";
import Sidebar from "./components/navigation/Sidebar";
import Container from "./components/layouts/Container";
import PageLayout from "./components/layouts/PageLayout";
import Card from "./components/Card";
import Table from "./components/Table";

// Create navbar with user dropdown
const navbar = Navbar.render({
  logo: '<img src="/logo.svg" alt="HealthBD" class="h-8 w-auto">',
  rightItems: [
    {
      type: "dropdown",
      icon: '<img src="/avatar.jpg" alt="User" class="h-8 w-8 rounded-full">',
      items: [
        { text: "Your Profile", href: "/profile" },
        { text: "Settings", href: "/settings" },
        { text: "Sign out", href: "/logout" },
      ],
    },
  ],
});

// Create sidebar
const sidebar = Sidebar.render({
  items: [
    {
      text: "Dashboard",
      href: "/dashboard",
      icon: '<i data-lucide="home" class="h-5 w-5"></i>',
      active: true,
    },
    {
      text: "Patients",
      href: "/patients",
      icon: '<i data-lucide="users" class="h-5 w-5"></i>',
    },
    {
      text: "Appointments",
      href: "/appointments",
      icon: '<i data-lucide="calendar" class="h-5 w-5"></i>',
    },
    {
      text: "Reports",
      href: "/reports",
      icon: '<i data-lucide="bar-chart" class="h-5 w-5"></i>',
    },
  ],
  footerItems: [
    {
      text: "Settings",
      href: "/settings",
      icon: '<i data-lucide="settings" class="h-5 w-5"></i>',
    },
    {
      text: "Help",
      href: "/help",
      icon: '<i data-lucide="help-circle" class="h-5 w-5"></i>',
    },
  ],
});

// Create dashboard content
const content = Container.render({
  content: `
    <div class="py-6">
      <h1 class="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        ${Card.render({
          title: "Total Patients",
          content:
            '<div class="text-3xl font-bold text-gray-900">1,248</div><div class="text-sm text-gray-500">+8% from last month</div>',
        })}
        ${Card.render({
          title: "Appointments Today",
          content:
            '<div class="text-3xl font-bold text-gray-900">24</div><div class="text-sm text-gray-500">4 pending</div>',
        })}
        ${Card.render({
          title: "Open Cases",
          content:
            '<div class="text-3xl font-bold text-gray-900">42</div><div class="text-sm text-gray-500">12 require attention</div>',
        })}
      </div>
      
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-900">Recent Patients</h2>
        </div>
        ${Table.render({
          headers: ["Name", "Date", "Status", "Action"],
          rows: [
            [
              "John Doe",
              "Today, 10:00 AM",
              '<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Active</span>',
              '<button class="text-cyan-600 hover:text-cyan-900">View</button>',
            ],
            [
              "Jane Smith",
              "Yesterday, 2:30 PM",
              '<span class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">Completed</span>',
              '<button class="text-cyan-600 hover:text-cyan-900">View</button>',
            ],
            [
              "Robert Johnson",
              "May 20, 9:15 AM",
              '<span class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">Pending</span>',
              '<button class="text-cyan-600 hover:text-cyan-900">View</button>',
            ],
          ],
          hoverable: true,
        })}
      </div>
    </div>
  `,
});

// Render the complete dashboard
const dashboard = PageLayout.dashboard({
  header: navbar,
  sidebar: sidebar,
  content: content,
  fixedHeader: true,
});

// Output the dashboard HTML
document.getElementById("app").innerHTML = dashboard;
```

## Contributing

When adding new components to the design system:

1. Follow the established [coding standards](./docs/coding-standards.md)
2. Ensure all components have proper documentation
3. Include usage examples in the component file
4. Update this documentation if needed

## License

This design system is proprietary and intended for use only within the HealthBD application.
