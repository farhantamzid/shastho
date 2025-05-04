/**
 * Table Component
 *
 * A reusable table component for displaying data in rows and columns.
 *
 * Usage:
 * ```
 * // Basic table
 * Table.render({
 *   headers: ['Name', 'Email', 'Role', 'Status'],
 *   rows: [
 *     ['John Doe', 'john@example.com', 'Doctor', 'Active'],
 *     ['Jane Smith', 'jane@example.com', 'Nurse', 'Inactive'],
 *     ['Robert Johnson', 'robert@example.com', 'Admin', 'Active']
 *   ]
 * });
 *
 * // Table with custom cell formatting
 * Table.render({
 *   headers: ['Name', 'Email', 'Role', 'Status'],
 *   rows: [
 *     [
 *       '<div class="flex items-center"><img src="/avatar.jpg" class="h-8 w-8 rounded-full mr-2"><span>John Doe</span></div>',
 *       'john@example.com',
 *       'Doctor',
 *       '<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Active</span>'
 *     ],
 *     // More rows...
 *   ],
 *   striped: true,
 *   hoverable: true
 * });
 * ```
 */

class Table {
  constructor() {
    this.baseClasses = "min-w-full divide-y divide-gray-300";
    this.headerClasses = "bg-gray-50";
    this.headerCellClasses =
      "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider";
    this.bodyClasses = "bg-white divide-y divide-gray-200";
    this.bodyCellClasses = "px-6 py-4 whitespace-nowrap text-sm text-gray-500";
  }

  /**
   * Renders a table with the specified options
   * @param {Object} options - Table options
   * @param {Array} options.headers - Array of header titles
   * @param {Array} options.rows - Array of row data (each row is an array of cells)
   * @param {boolean} options.striped - Whether to apply striped rows
   * @param {boolean} options.hoverable - Whether to apply hover effect on rows
   * @param {boolean} options.bordered - Whether to add borders to the table
   * @param {boolean} options.compact - Whether to use compact padding
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the table
   */
  render({
    headers = [],
    rows = [],
    striped = false,
    hoverable = false,
    bordered = false,
    compact = false,
    className = "",
  }) {
    // Determine cell padding based on compact option
    const cellPadding = compact ? "px-3 py-2" : "px-6 py-4";

    // Adjust header cell classes
    const headerCellClasses = [
      compact ? "px-3 py-2" : "px-6 py-3",
      "text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
    ].join(" ");

    // Adjust body cell classes
    const bodyCellClasses = [
      cellPadding,
      "whitespace-nowrap text-sm text-gray-500",
    ].join(" ");

    // Generate HTML for the table header
    const headerHtml = headers.length
      ? `
        <thead class="${this.headerClasses}">
          <tr>
            ${headers
              .map(
                (header) => `
                <th scope="col" class="${headerCellClasses}">
                  ${header}
                </th>
              `
              )
              .join("")}
          </tr>
        </thead>
      `
      : "";

    // Generate HTML for the table body
    const bodyHtml = rows.length
      ? `
        <tbody class="${this.bodyClasses} ${
          striped ? "divide-y divide-gray-200" : "divide-y divide-gray-200"
        }">
          ${rows
            .map(
              (row, rowIndex) => `
              <tr class="${striped && rowIndex % 2 === 1 ? "bg-gray-50" : ""} ${
                hoverable ? "hover:bg-gray-100" : ""
              }">
                ${row
                  .map(
                    (cell, cellIndex) => `
                    <td class="${bodyCellClasses} ${
                      cellIndex === 0 ? "font-medium text-gray-900" : ""
                    }">
                      ${cell}
                    </td>
                  `
                  )
                  .join("")}
              </tr>
            `
            )
            .join("")}
        </tbody>
      `
      : "";

    // Combine all table classes
    const tableClasses = [
      this.baseClasses,
      bordered ? "border border-gray-300" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Build the complete table HTML with responsive wrapper
    return `
      <div class="flex flex-col">
        <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table class="${tableClasses}">
                ${headerHtml}
                ${bodyHtml}
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Creates a striped table
   * @param {Object} options - Table options
   * @returns {string} HTML markup for a striped table
   */
  striped(options) {
    return this.render({ striped: true, ...options });
  }

  /**
   * Creates a hoverable table
   * @param {Object} options - Table options
   * @returns {string} HTML markup for a hoverable table
   */
  hoverable(options) {
    return this.render({ hoverable: true, ...options });
  }

  /**
   * Creates a compact table with reduced padding
   * @param {Object} options - Table options
   * @returns {string} HTML markup for a compact table
   */
  compact(options) {
    return this.render({ compact: true, ...options });
  }

  /**
   * Creates a bordered table
   * @param {Object} options - Table options
   * @returns {string} HTML markup for a bordered table
   */
  bordered(options) {
    return this.render({ bordered: true, ...options });
  }
}

// Export the Table class
export default new Table();
