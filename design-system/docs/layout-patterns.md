# Layout Patterns and Templates

This document outlines the standard layout patterns and templates used throughout the HealthBD application.

## Layout Components

### PageLayout

The `PageLayout` component provides consistent page structure across the application.

#### Types of Layouts

1. **Default Layout**

   - Used for standard pages with a header, main content area, and optional footer
   - Typically used for content-focused pages

   ```javascript
   PageLayout.render({
     header: Navbar.render({ ... }),
     content: `<div class="py-6">Page content here</div>`,
     footer: `<footer class="p-4 border-t">Footer content</footer>`
   });
   ```

2. **Dashboard Layout**

   - Used for pages with sidebar navigation
   - Includes support for fixed header and responsive sidebar
   - Ideal for admin interfaces, dashboard sections, and account management

   ```javascript
   PageLayout.render({
     type: 'dashboard',
     header: Navbar.render({ ... }),
     sidebar: Sidebar.render({ ... }),
     content: `<div class="py-6">Dashboard content</div>`,
     fixedHeader: true
   });
   ```

3. **Authentication Layout**

   - Used for login, registration, and other authentication-related pages
   - Centers content in a narrower card-like container
   - Optionally includes header and footer

   ```javascript
   PageLayout.render({
     type: "auth",
     content: `<div>Authentication form here</div>`,
   });
   ```

### Container

The `Container` component provides consistent width constraints and padding for content.

#### Container Sizes

- **XS** (`xs`): 20rem (320px)
- **SM** (`sm`): 24rem (384px)
- **MD** (`md`): 28rem (448px)
- **LG** (`lg`): 32rem (512px)
- **XL** (`xl`): 36rem (576px)
- **2XL** (`2xl`): 42rem (672px)
- **3XL** (`3xl`): 48rem (768px)
- **4XL** (`4xl`): 56rem (896px)
- **5XL** (`5xl`): 64rem (1024px)
- **6XL** (`6xl`): 72rem (1152px)
- **7XL** (`7xl`): 80rem (1280px)
- **Narrow** (`narrow`): Alias for 3XL (48rem/768px)
- **Default** (`default`): 7XL (80rem/1280px)
- **Wide** (`wide`): screen-2xl
- **Full** (`full`): No max-width constraint

#### Usage Examples

```javascript
// Default container
Container.render({
  content: `<p>Content with standard max-width and padding</p>`,
});

// Narrow container
Container.narrow({
  content: `<p>Narrower content (max-w-3xl)</p>`,
});

// Centered text container
Container.centered({
  content: `<p>This text will be centered</p>`,
});
```

### Grid

The `Grid` component provides a convenient way to create responsive grid layouts.

#### Column Configuration

- **Fixed Columns**: `columns: 3` (1-12 columns)
- **Responsive Columns**:
  ```javascript
  columns: {
    default: 1, // Mobile (all screens by default)
    sm: 2,      // Small screens (640px+)
    md: 3,      // Medium screens (768px+)
    lg: 4       // Large screens (1024px+)
  }
  ```

#### Gap Sizes

Standard Tailwind gap sizes (1-12) can be used.

#### Usage Examples

```javascript
// Basic 3-column grid
Grid.render({
  columns: 3,
  gap: 6,
  items: [
    '<div class="p-4 bg-white shadow rounded-lg">Item 1</div>',
    '<div class="p-4 bg-white shadow rounded-lg">Item 2</div>',
    '<div class="p-4 bg-white shadow rounded-lg">Item 3</div>',
  ],
});

// Responsive grid
Grid.responsive({
  gap: 4,
  items: [
    '<div class="p-4 bg-white shadow rounded-lg">Item 1</div>',
    '<div class="p-4 bg-white shadow rounded-lg">Item 2</div>',
    '<div class="p-4 bg-white shadow rounded-lg">Item 3</div>',
    '<div class="p-4 bg-white shadow rounded-lg">Item 4</div>',
  ],
});
```

## Common Page Patterns

### Dashboard Page Pattern

```html
<!-- Dashboard Layout -->
<div class="min-h-screen bg-gray-50">
  <!-- Fixed Header -->
  <div class="fixed top-0 left-0 right-0 z-10">
    <!-- Navbar -->
  </div>

  <div class="flex pt-16">
    <!-- Sidebar (Hidden on mobile) -->
    <div
      class="w-64 bg-white border-r border-gray-200 hidden md:flex md:flex-col"
    >
      <!-- Sidebar Content -->
    </div>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto md:ml-64">
      <div class="py-6">
        <!-- Page Header -->
        <div class="mx-auto px-4 sm:px-6 lg:px-8">
          <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>
        </div>

        <!-- Page Content -->
        <div class="mx-auto px-4 sm:px-6 lg:px-8 mt-6">
          <!-- Content goes here -->
        </div>
      </div>
    </main>
  </div>
</div>
```

### Authentication Page Pattern

```html
<!-- Auth Layout -->
<div
  class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8"
>
  <!-- Header (Optional) -->
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <img class="mx-auto h-12 w-auto" src="/logo.svg" alt="Logo" />
    <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
      Sign in to your account
    </h2>
  </div>

  <!-- Auth Form Container -->
  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
    <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
      <!-- Form content goes here -->
    </div>
  </div>
</div>
```

### Content Page Pattern

```html
<!-- Default Layout -->
<div class="min-h-screen bg-gray-50 flex flex-col">
  <!-- Header -->
  <header class="bg-white shadow">
    <!-- Navbar -->
  </header>

  <!-- Main Content -->
  <main class="flex-1">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 class="text-2xl font-semibold text-gray-900">Page Title</h1>
      </div>
    </div>

    <!-- Page Content -->
    <div class="mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-white shadow sm:rounded-lg p-6">
        <!-- Content goes here -->
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="bg-white border-t border-gray-200">
    <div class="mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <!-- Footer content -->
    </div>
  </footer>
</div>
```

## Responsive Behavior

All layout components are designed with a mobile-first approach:

1. **Mobile (Default)**

   - Single column layout
   - Sidebar hidden
   - Full-width containers
   - Stacked elements

2. **Small Screens (sm: 640px+)**

   - Enhanced padding
   - 2-column grids where appropriate
   - Centered containers with margins

3. **Medium Screens (md: 768px+)**

   - Sidebar appears
   - Multi-column layouts
   - 3-column grids where appropriate

4. **Large Screens (lg: 1024px+)**

   - Further enhanced padding
   - Potentially 4-column grids
   - Full layout features

5. **Extra Large Screens (xl: 1280px+)**
   - Maximum content width constraints
   - Optimized spacing

## Best Practices

1. **Always use the appropriate layout component** for the page type
2. **Use containers inside content areas** to maintain consistent width constraints
3. **Leverage the grid system** for responsive column layouts instead of custom solutions
4. **Follow the mobile-first approach** by designing for mobile and then enhancing for larger screens
5. **Maintain consistent spacing** throughout the application
6. **Use the responsive Tailwind utility classes** (sm:, md:, lg:, xl:) to adjust layouts at different breakpoints
