/**
 * Grid Component
 *
 * A reusable grid component for creating responsive grid layouts.
 *
 * Usage:
 * ```
 * // Basic 3-column grid
 * Grid.render({
 *   columns: 3,
 *   gap: 6,
 *   items: [
 *     '<div class="p-4 bg-white shadow rounded-lg">Item 1</div>',
 *     '<div class="p-4 bg-white shadow rounded-lg">Item 2</div>',
 *     '<div class="p-4 bg-white shadow rounded-lg">Item 3</div>',
 *     '<div class="p-4 bg-white shadow rounded-lg">Item 4</div>',
 *     '<div class="p-4 bg-white shadow rounded-lg">Item 5</div>',
 *     '<div class="p-4 bg-white shadow rounded-lg">Item 6</div>'
 *   ]
 * });
 *
 * // Responsive grid with different column counts at different breakpoints
 * Grid.render({
 *   columns: {
 *     default: 1,
 *     sm: 2,
 *     md: 3,
 *     lg: 4
 *   },
 *   gap: 4,
 *   items: [...]
 * });
 * ```
 */

class Grid {
  constructor() {
    this.baseClasses = "grid";
  }

  /**
   * Renders a grid with the specified options
   * @param {Object|number} options.columns - Number of columns or object with breakpoint-specific values
   * @param {number|string} options.gap - Gap size (1-12) or gap class name
   * @param {Array} options.items - Array of grid item HTML strings
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the grid
   */
  render({ columns = 1, gap = 4, items = [], className = "" }) {
    // Process columns configuration
    let columnsClasses = "";

    if (typeof columns === "number") {
      // Handle simple numeric columns
      columnsClasses = this.getColumnsClass(columns);
    } else if (typeof columns === "object") {
      // Handle responsive columns object
      const columnEntries = Object.entries(columns);

      columnsClasses = columnEntries
        .map(([breakpoint, cols]) => {
          // Default breakpoint doesn't have a prefix
          const prefix = breakpoint === "default" ? "" : `${breakpoint}:`;
          return `${prefix}${this.getColumnsClass(cols)}`;
        })
        .join(" ");
    }

    // Process gap
    let gapClass = "";
    if (typeof gap === "number") {
      gapClass = `gap-${gap}`;
    } else if (typeof gap === "string") {
      gapClass = gap;
    }

    // Combine grid classes
    const gridClasses = [this.baseClasses, columnsClasses, gapClass, className]
      .filter(Boolean)
      .join(" ");

    // Generate grid items HTML
    const itemsHtml = items.map((item) => `<div>${item}</div>`).join("");

    // Build the complete grid HTML
    return `
      <div class="${gridClasses}">
        ${itemsHtml}
      </div>
    `;
  }

  /**
   * Get the Tailwind CSS class for a specific column count
   * @param {number} columns - Number of columns
   * @returns {string} Tailwind CSS grid template columns class
   */
  getColumnsClass(columns) {
    // Map common column counts to Tailwind's grid-cols-* classes
    const colsMap = {
      1: "grid-cols-1",
      2: "grid-cols-2",
      3: "grid-cols-3",
      4: "grid-cols-4",
      5: "grid-cols-5",
      6: "grid-cols-6",
      7: "grid-cols-7",
      8: "grid-cols-8",
      9: "grid-cols-9",
      10: "grid-cols-10",
      11: "grid-cols-11",
      12: "grid-cols-12",
    };

    return colsMap[columns] || "grid-cols-1";
  }

  /**
   * Creates a two-column grid
   * @param {Object} options - Grid options
   * @returns {string} HTML markup for a two-column grid
   */
  cols2(options) {
    return this.render({ columns: 2, ...options });
  }

  /**
   * Creates a three-column grid
   * @param {Object} options - Grid options
   * @returns {string} HTML markup for a three-column grid
   */
  cols3(options) {
    return this.render({ columns: 3, ...options });
  }

  /**
   * Creates a four-column grid
   * @param {Object} options - Grid options
   * @returns {string} HTML markup for a four-column grid
   */
  cols4(options) {
    return this.render({ columns: 4, ...options });
  }

  /**
   * Creates a responsive grid that adapts to different screen sizes
   * @param {Object} options - Grid options
   * @returns {string} HTML markup for a responsive grid
   */
  responsive(options) {
    return this.render({
      columns: {
        default: 1,
        sm: 2,
        md: 3,
        lg: 4,
      },
      ...options,
    });
  }
}

// Export the Grid class
export default new Grid();
