"""
Card component that adheres to the shastho design system.
"""

def basic(content, title=None, footer=None, variant="default"):
    """
    Generate HTML for a basic card.

    Args:
        content (str): Main content HTML for the card body
        title (str): Optional card title/header
        footer (str): Optional card footer
        variant (str): Card style variant (default, borderless, interactive)

    Returns:
        str: HTML for the card
    """
    # Base classes based on variant
    variant_classes = {
        "default": "bg-white border border-gray-200 rounded-xl shadow-sm",
        "borderless": "bg-white rounded-xl shadow-sm",
        "interactive": "bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer"
    }

    classes = variant_classes.get(variant, variant_classes["default"])

    # Build the card HTML
    html = f'<div class="{classes}">'

    # Add title/header if provided
    if title:
        html += f'<div class="px-6 py-4 border-b border-gray-100">'
        html += f'<h3 class="text-lg font-semibold text-gray-900">{title}</h3>'
        html += '</div>'

    # Add main content
    html += f'<div class="p-6">{content}</div>'

    # Add footer if provided
    if footer:
        html += f'<div class="px-6 py-4 bg-gray-50 rounded-b-xl border-t border-gray-100">{footer}</div>'

    html += '</div>'

    return html

def action_card(title, description, action_text, action_url="#", icon=None):
    """
    Generate HTML for an action card with a title, description and button.

    Args:
        title (str): Card title
        description (str): Card description text
        action_text (str): Text for the action button
        action_url (str): URL for the action button
        icon (str): Optional HTML for an icon

    Returns:
        str: HTML for the action card
    """
    # Icon HTML if provided
    icon_html = f'<div class="text-primary mb-4">{icon}</div>' if icon else ''

    # Card content with title, description and button
    content = f"""
        {icon_html}
        <h3 class="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        <p class="text-gray-600 mb-4">{description}</p>
        <a href="{action_url}" class="inline-block bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-lg font-medium transition-colors">
            {action_text}
        </a>
    """

    return basic(content, variant="interactive")

def stat_card(value, label, trend=None, trend_direction=None):
    """
    Generate HTML for a statistics card.

    Args:
        value (str): The main statistic value
        label (str): Description of the statistic
        trend (str): Optional trend value (e.g., "+12%")
        trend_direction (str): Direction of trend ('up', 'down', or None)

    Returns:
        str: HTML for the statistics card
    """
    # Define trend colors and icons
    trend_html = ''
    if trend:
        if trend_direction == 'up':
            trend_html = f'<span class="text-success flex items-center ml-2"><svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg> {trend}</span>'
        elif trend_direction == 'down':
            trend_html = f'<span class="text-error flex items-center ml-2"><svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg> {trend}</span>'
        else:
            trend_html = f'<span class="text-gray-500 ml-2">{trend}</span>'

    # Card content
    content = f"""
        <div>
            <p class="text-gray-500 text-sm mb-1">{label}</p>
            <div class="flex items-center">
                <span class="text-2xl font-bold text-gray-900">{value}</span>
                {trend_html}
            </div>
        </div>
    """

    return basic(content, variant="borderless")