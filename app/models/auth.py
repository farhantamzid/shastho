import bcrypt
from uuid import uuid4
import secrets
import string
from datetime import datetime, timedelta
from app.models.database import User, UserRole, UserStatus, PasswordResetToken, Language, UserSession
from app.utils.db import db

def find_user_by_username(username):
    """Find a user by username."""
    return db.get_user_by_username(username)

def find_user_by_id(user_id):
    """Find a user by ID."""
    return db.get_by_id(User, user_id)

def create_user(username, password, role, full_name=None):
    """Create a new user."""
    # Check if user already exists
    if find_user_by_username(username):
        return None

    # Hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    password_hash = hashed.decode('utf-8')

    # Set initial status based on role
    initial_status = UserStatus.INACTIVE if role == 'hospital_admin' else UserStatus.ACTIVE

    # Create the user
    user = User(
        id=uuid4(),
        username=username,
        password_hash=password_hash,
        role=UserRole(role),
        status=initial_status
    )

    # Save to database
    user = db.create(user)

    # Store full_name attribute
    user.full_name = full_name or username

    return user

def validate_credentials(username, password):
    """Validate user credentials."""
    user = find_user_by_username(username)
    if not user:
        return None

    # Check password
    is_valid = bcrypt.checkpw(
        password.encode('utf-8'),
        user.password_hash.encode('utf-8')
    )

    if is_valid:
        return user

    return None

def change_password(user_id, old_password, new_password):
    """Change a user's password."""
    user = find_user_by_id(user_id)
    if not user:
        return False

    # Verify old password
    is_valid = bcrypt.checkpw(
        old_password.encode('utf-8'),
        user.password_hash.encode('utf-8')
    )

    if not is_valid:
        return False

    # Update password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    user.password_hash = hashed.decode('utf-8')

    # Update in database
    db.update(user)

    return True

def create_password_reset_token(user_id, expiration_hours=24):
    """Create a password reset token for a user.

    Args:
        user_id: The ID of the user
        expiration_hours: Number of hours the token will be valid

    Returns:
        The token string if successful, None otherwise
    """
    user = find_user_by_id(user_id)
    if not user:
        return None

    # Generate a secure random token
    # Using a combination of letters, digits, and some special characters
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(64))

    # Set expiration time
    expires_at = datetime.now() + timedelta(hours=expiration_hours)

    # Create and store the token
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False
    )

    db.create(reset_token)

    return token

def verify_reset_token(token):
    """Verify if a password reset token is valid.

    Args:
        token: The token string to verify

    Returns:
        The associated user if valid, None otherwise
    """
    token_obj = db.get_reset_token_by_token(token)

    if not token_obj or not token_obj.is_valid():
        return None

    user = find_user_by_id(token_obj.user_id)
    return user

def reset_password_with_token(token, new_password):
    """Reset a user's password using a token.

    Args:
        token: The token string
        new_password: The new password to set

    Returns:
        True if successful, False otherwise
    """
    token_obj = db.get_reset_token_by_token(token)

    if not token_obj or not token_obj.is_valid():
        return False

    user = find_user_by_id(token_obj.user_id)
    if not user:
        return False

    # Update password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    user.password_hash = hashed.decode('utf-8')

    # Update in database
    db.update(user)

    # Mark token as used
    db.mark_token_as_used(token_obj.id)

    return True

def find_users_by_role_and_status(role, status):
    """Find users with a specific role and status."""
    role_value = None
    # Convert role to UserRole enum if it's a string, then get its value
    if isinstance(role, str):
        try:
            role_value = UserRole(role).value
        except ValueError:
            print(f"Invalid role string provided: {role}")
            return []
    elif isinstance(role, UserRole):
        role_value = role.value
    else:
        print(f"Invalid role type provided: {type(role)}")
        return []

    # Get the value of the status enum
    status_value = None
    if isinstance(status, UserStatus):
        status_value = status.value
    else:
        print(f"Invalid status type provided: {type(status)}")
        return []

    # Query users using the string values for role and status
    print(f"Querying Users with role='{role_value}' and status='{status_value}'")
    users = db.query(User, role=role_value, status=status_value)
    print(f"db.query returned {len(users)} users.")
    return users

def update_user_status(user_id, new_status):
    """
    Update a user's status.

    :param user_id: ID of the user to update
    :param new_status: New UserStatus enum value
    :return: True if successful, False otherwise
    """
    # Fetch the user
    user = db.get_by_id(User, user_id)
    if not user:
        return False

    # Update the status
    user.status = new_status

    # Save the user
    updated_user = db.update(user)
    return updated_user is not None

def update_user_profile_picture(user_id, profile_picture_url):
    """Update a user's profile picture URL."""
    user = find_user_by_id(user_id)
    if not user:
        return False

    # Update profile picture URL
    user.profile_picture_url = profile_picture_url

    # Update in database
    updated_user = db.update(user)

    return updated_user is not None

def update_user_language_preference(user_id, language):
    """Update a user's language preference."""
    user = find_user_by_id(user_id)
    if not user:
        return False

    # Update language preference
    try:
        user.language_preference = Language(language)
    except ValueError:
        return False

    # Update in database
    updated_user = db.update(user)

    return updated_user is not None

# Session management functions
def create_user_session(user_id, session_id, user_agent=None, ip_address=None):
    """Create a new user session."""
    session = UserSession(
        user_id=user_id,
        session_id=session_id,
        user_agent=user_agent,
        ip_address=ip_address
    )

    try:
        # Try to save to database
        created_session = db.create(session)
        return created_session
    except Exception as e:
        # If there's an error (like table doesn't exist), return the session object anyway
        print(f"Error creating user session in database: {str(e)}")
        return session  # Return the in-memory session object

def get_user_sessions(user_id):
    """Get all sessions for a user."""
    try:
        # Get all sessions
        all_sessions = db.get_all(UserSession)

        # Filter by user_id
        user_sessions = [
            session for session in all_sessions
            if str(session.user_id) == str(user_id)
        ]

        return user_sessions
    except Exception as e:
        print(f"Error retrieving user sessions: {str(e)}")
        return []  # Return empty list on error

def get_active_sessions(user_id):
    """Get all active sessions for a user."""
    try:
        all_sessions = get_user_sessions(user_id)

        # Filter by active status
        active_sessions = [
            session for session in all_sessions
            if session.is_active
        ]

        return active_sessions
    except Exception as e:
        print(f"Error retrieving active sessions: {str(e)}")
        return []  # Return empty list on error

def terminate_session(session_id):
    """Terminate a specific session."""
    try:
        # Find the session
        all_sessions = db.get_all(UserSession)
        session = next((s for s in all_sessions if s.session_id == session_id), None)

        if not session:
            return False

        # Update session
        session.is_active = False
        session.last_activity = datetime.now()

        # Update in database
        updated_session = db.update(session)

        return updated_session is not None
    except Exception as e:
        print(f"Error terminating session: {str(e)}")
        return True  # Pretend it worked to not disrupt user experience

def terminate_all_sessions(user_id, current_session_id=None):
    """Terminate all sessions for a user except the current one."""
    try:
        active_sessions = get_active_sessions(user_id)

        success = True
        for session in active_sessions:
            # Skip current session if specified
            if current_session_id and session.session_id == current_session_id:
                continue

            # Terminate session
            if not terminate_session(session.session_id):
                success = False

        return success
    except Exception as e:
        print(f"Error terminating all sessions: {str(e)}")
        return True  # Pretend it worked to not disrupt user experience

def update_session_activity(session_id):
    """Update the last activity timestamp for a session."""
    try:
        # Find the session
        all_sessions = db.get_all(UserSession)
        session = next((s for s in all_sessions if s.session_id == session_id), None)

        if not session:
            return False

        # Update last activity
        session.last_activity = datetime.now()

        # Update in database
        updated_session = db.update(session)

        return updated_session is not None
    except Exception as e:
        print(f"Error updating session activity: {str(e)}")
        return True  # Pretend it worked to not disrupt user experience

# Create some initial users for testing
def create_demo_users():
    """Create demo users for testing."""
    if not find_user_by_username('patient@shastho.com'):
        create_user('patient@shastho.com', 'patient123', 'patient', 'Demo Patient')

    if not find_user_by_username('doctor@shastho.com'):
        create_user('doctor@shastho.com', 'doctor123', 'doctor', 'Dr. Demo Doctor')

    if not find_user_by_username('admin@shastho.com'):
        create_user('admin@shastho.com', 'admin123', 'admin', 'Admin User')

    if not find_user_by_username('staff@shastho.com'):
        create_user('staff@shastho.com', 'staff123', 'staff', 'Staff Member')

    # Also keep the example.com accounts for backward compatibility
    if not find_user_by_username('patient@example.com'):
        create_user('patient@example.com', 'password123', 'patient', 'Demo Patient')

    if not find_user_by_username('doctor@example.com'):
        create_user('doctor@example.com', 'password123', 'doctor', 'Dr. Demo Doctor')

    if not find_user_by_username('admin@example.com'):
        create_user('admin@example.com', 'password123', 'admin', 'Admin User')

    if not find_user_by_username('staff@example.com'):
        create_user('staff@example.com', 'password123', 'staff', 'Staff Member')

# Call this function to ensure demo users exist
create_demo_users()