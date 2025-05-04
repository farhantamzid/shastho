import bcrypt
from uuid import uuid4
from app.models.database import User, UserRole, UserStatus
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

    # Create the user
    user = User(
        id=uuid4(),
        username=username,
        password_hash=password_hash,
        role=UserRole(role),
        status=UserStatus.ACTIVE
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