from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from app.models.database import UserRole
from app.utils.auth import login_required, role_required
from app.utils.db import Database
from app.models.audit import AuditLog, AuditActionType, AuditResourceType
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')
db = Database()

@audit_bp.route('/logs')
@login_required
@role_required(UserRole.HOSPITAL_ADMIN)
def view_logs():
    """View audit logs with filtering options"""
    # Get filter parameters
    action_type = request.args.get('action_type')
    resource_type = request.args.get('resource_type')
    user_id = request.args.get('user_id')
    resource_id = request.args.get('resource_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to last 7 days if no date range specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # Convert string dates to datetime objects
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the end date

    # Get all audit logs
    audit_logs = db.get_all(AuditLog)

    # Apply filters
    filtered_logs = []
    for log in audit_logs:
        # Skip logs outside the date range
        if log.timestamp < start_datetime or log.timestamp > end_datetime:
            continue

        # Apply action type filter if specified
        if action_type and log.action and log.action.value != action_type:
            continue

        # Apply resource type filter if specified
        if resource_type and log.resource_type and log.resource_type.value != resource_type:
            continue

        # Apply user ID filter if specified
        if user_id and str(log.user_id) != user_id:
            continue

        # Apply resource ID filter if specified
        if resource_id and str(log.resource_id) != resource_id:
            continue

        filtered_logs.append(log)

    # Sort logs by timestamp (newest first)
    filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)

    # Get users for the user filter dropdown
    users = []
    try:
        from app.models.database import User
        all_users = db.get_all(User)
        users = [{'id': str(user.id), 'username': user.username} for user in all_users]
    except Exception as e:
        flash(f"Error loading users: {str(e)}", 'error')

    # Prepare values for filter dropdowns
    action_types = [{'value': action.value, 'label': action.value.capitalize()} for action in AuditActionType]
    resource_types = [{'value': res.value, 'label': res.value.replace('_', ' ').capitalize()} for res in AuditResourceType]

    return render_template(
        'admin/audit/logs.html',
        logs=filtered_logs,
        action_types=action_types,
        resource_types=resource_types,
        users=users,
        filters={
            'action_type': action_type,
            'resource_type': resource_type,
            'user_id': user_id,
            'resource_id': resource_id,
            'start_date': start_date,
            'end_date': end_date
        }
    )

@audit_bp.route('/logs/details/<uuid:log_id>')
@login_required
@role_required(UserRole.HOSPITAL_ADMIN)
def log_details(log_id):
    """View detailed information for a specific audit log entry"""
    # Get the log
    audit_log = db.get_by_id(AuditLog, log_id)

    if not audit_log:
        flash('Audit log not found.', 'error')
        return redirect(url_for('audit.view_logs'))

    # Get user information
    user = None
    if audit_log.user_id:
        from app.models.database import User
        user = db.get_by_id(User, audit_log.user_id)

    # Get resource information based on resource type
    resource = None
    if audit_log.resource_id and audit_log.resource_type:
        try:
            if audit_log.resource_type == AuditResourceType.PATIENT:
                from app.models.database import Patient
                resource = db.get_by_id(Patient, audit_log.resource_id)
            elif audit_log.resource_type == AuditResourceType.DOCTOR:
                from app.models.database import Doctor
                resource = db.get_by_id(Doctor, audit_log.resource_id)
            elif audit_log.resource_type == AuditResourceType.HOSPITAL_ADMIN:
                from app.models.database import HospitalAdmin
                resource = db.get_by_id(HospitalAdmin, audit_log.resource_id)
            elif audit_log.resource_type == AuditResourceType.USER:
                from app.models.database import User
                resource = db.get_by_id(User, audit_log.resource_id)
            # Add more resource types as needed
        except Exception as e:
            flash(f"Error loading resource: {str(e)}", 'warning')

    return render_template(
        'admin/audit/log_details.html',
        log=audit_log,
        user=user,
        resource=resource
    )

@audit_bp.route('/reports/activity')
@login_required
@role_required(UserRole.HOSPITAL_ADMIN)
def activity_report():
    """Generate activity reports based on audit logs"""
    # Get filter parameters
    report_type = request.args.get('type', 'daily')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to last 30 days if no date range specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # Convert string dates to datetime objects
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the end date

    # Get all audit logs
    audit_logs = db.get_all(AuditLog)

    # Filter logs by date range
    filtered_logs = [log for log in audit_logs if start_datetime <= log.timestamp <= end_datetime]

    # Generate report data
    report_data = {}

    if report_type == 'daily':
        # Group by day
        report_data = generate_daily_report(filtered_logs)
    elif report_type == 'user':
        # Group by user
        report_data = generate_user_report(filtered_logs)
    elif report_type == 'resource':
        # Group by resource type
        report_data = generate_resource_report(filtered_logs)
    elif report_type == 'action':
        # Group by action type
        report_data = generate_action_report(filtered_logs)

    return render_template(
        'admin/audit/activity_report.html',
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        report_data=report_data
    )

@audit_bp.route('/api/logs')
@login_required
@role_required(UserRole.HOSPITAL_ADMIN)
def api_logs():
    """API endpoint to fetch audit logs as JSON"""
    # Get filter parameters (similar to view_logs but returns JSON)
    action_type = request.args.get('action_type')
    resource_type = request.args.get('resource_type')
    user_id = request.args.get('user_id')
    resource_id = request.args.get('resource_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to last 7 days if no date range specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # Convert string dates to datetime objects
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the end date

    # Get all audit logs
    audit_logs = db.get_all(AuditLog)

    # Apply filters
    filtered_logs = []
    for log in audit_logs:
        # Skip logs outside the date range
        if log.timestamp < start_datetime or log.timestamp > end_datetime:
            continue

        # Apply action type filter if specified
        if action_type and log.action and log.action.value != action_type:
            continue

        # Apply resource type filter if specified
        if resource_type and log.resource_type and log.resource_type.value != resource_type:
            continue

        # Apply user ID filter if specified
        if user_id and str(log.user_id) != user_id:
            continue

        # Apply resource ID filter if specified
        if resource_id and str(log.resource_id) != resource_id:
            continue

        filtered_logs.append(log.to_dict())

    # Sort logs by timestamp (newest first)
    filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)

    return jsonify({
        'status': 'success',
        'count': len(filtered_logs),
        'logs': filtered_logs
    })

# Helper functions for report generation

def generate_daily_report(logs: List[AuditLog]) -> Dict[str, Any]:
    """Generate a report of activity by day"""
    daily_data = {}

    for log in logs:
        day = log.timestamp.strftime('%Y-%m-%d')
        if day not in daily_data:
            daily_data[day] = {'total': 0, 'successful': 0, 'failed': 0}

        daily_data[day]['total'] += 1
        if log.success:
            daily_data[day]['successful'] += 1
        else:
            daily_data[day]['failed'] += 1

    # Convert to sorted list for the template
    sorted_data = [
        {'date': day, 'total': data['total'], 'successful': data['successful'], 'failed': data['failed']}
        for day, data in sorted(daily_data.items())
    ]

    return {
        'title': 'Daily Activity Report',
        'columns': ['Date', 'Total Actions', 'Successful', 'Failed'],
        'data': sorted_data
    }

def generate_user_report(logs: List[AuditLog]) -> Dict[str, Any]:
    """Generate a report of activity by user"""
    user_data = {}

    # Get all users for mapping
    try:
        from app.models.database import User
        all_users = db.get_all(User)
        users_map = {str(user.id): user.username for user in all_users}
    except:
        users_map = {}

    for log in logs:
        user_id = str(log.user_id) if log.user_id else 'unknown'
        username = users_map.get(user_id, user_id)

        if username not in user_data:
            user_data[username] = {
                'total': 0,
                'create': 0,
                'read': 0,
                'update': 0,
                'delete': 0,
                'login': 0,
                'logout': 0,
                'failed': 0
            }

        user_data[username]['total'] += 1

        # Count by action type
        if log.action:
            action_type = log.action.value
            if action_type in user_data[username]:
                user_data[username][action_type] += 1

        # Count failures
        if not log.success:
            user_data[username]['failed'] += 1

    # Convert to sorted list for the template
    sorted_data = [
        {
            'username': username,
            'total': data['total'],
            'create': data['create'],
            'read': data['read'],
            'update': data['update'],
            'delete': data['delete'],
            'login': data['login'],
            'logout': data['logout'],
            'failed': data['failed']
        }
        for username, data in sorted(user_data.items(), key=lambda x: x[1]['total'], reverse=True)
    ]

    return {
        'title': 'User Activity Report',
        'columns': ['Username', 'Total', 'Create', 'Read', 'Update', 'Delete', 'Login', 'Logout', 'Failed'],
        'data': sorted_data
    }

def generate_resource_report(logs: List[AuditLog]) -> Dict[str, Any]:
    """Generate a report of activity by resource type"""
    resource_data = {}

    for log in logs:
        resource_type = log.resource_type.value if log.resource_type else 'unknown'

        if resource_type not in resource_data:
            resource_data[resource_type] = {
                'total': 0,
                'create': 0,
                'read': 0,
                'update': 0,
                'delete': 0,
                'failed': 0
            }

        resource_data[resource_type]['total'] += 1

        # Count by action type
        if log.action:
            action_type = log.action.value
            if action_type in resource_data[resource_type]:
                resource_data[resource_type][action_type] += 1

        # Count failures
        if not log.success:
            resource_data[resource_type]['failed'] += 1

    # Convert to sorted list for the template
    sorted_data = [
        {
            'resource_type': resource_type.replace('_', ' ').capitalize(),
            'total': data['total'],
            'create': data['create'],
            'read': data['read'],
            'update': data['update'],
            'delete': data['delete'],
            'failed': data['failed']
        }
        for resource_type, data in sorted(resource_data.items(), key=lambda x: x[1]['total'], reverse=True)
    ]

    return {
        'title': 'Resource Type Activity Report',
        'columns': ['Resource Type', 'Total', 'Create', 'Read', 'Update', 'Delete', 'Failed'],
        'data': sorted_data
    }

def generate_action_report(logs: List[AuditLog]) -> Dict[str, Any]:
    """Generate a report of activity by action type"""
    action_data = {}

    for log in logs:
        action_type = log.action.value if log.action else 'unknown'

        if action_type not in action_data:
            action_data[action_type] = {
                'total': 0,
                'successful': 0,
                'failed': 0
            }

        action_data[action_type]['total'] += 1

        # Count successes and failures
        if log.success:
            action_data[action_type]['successful'] += 1
        else:
            action_data[action_type]['failed'] += 1

    # Convert to sorted list for the template
    sorted_data = [
        {
            'action_type': action_type.replace('_', ' ').capitalize(),
            'total': data['total'],
            'successful': data['successful'],
            'failed': data['failed'],
            'success_rate': f"{data['successful'] / data['total'] * 100:.1f}%" if data['total'] > 0 else "0%"
        }
        for action_type, data in sorted(action_data.items(), key=lambda x: x[1]['total'], reverse=True)
    ]

    return {
        'title': 'Action Type Report',
        'columns': ['Action Type', 'Total', 'Successful', 'Failed', 'Success Rate'],
        'data': sorted_data
    }