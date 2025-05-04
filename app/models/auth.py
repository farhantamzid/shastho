import bcrypt
from uuid import uuid4
from app.models.database import User, UserRole, UserStatus

# Mock database for users - in a real implementation, this would be a database
# Will be replaced by a database in future tasks
users_db = {}

def find_user_by_username(username):
    """Find a user by username."""
    for user_id, user in users_db.items():
        if user.username == username:
            return user
    return None

def find_user_by_id(user_id):
    """Find a user by ID."""
    return users_db.get(str(user_id))

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

    # Add full_name attribute to user object
    user.full_name = full_name or username

    # Save to our mock database
    users_db[str(user.id)] = user

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

    # Update in mock database
    users_db[str(user.id)] = user

    return True

# Create some initial users for testing
def create_demo_users():
    """Create demo users for testing."""
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