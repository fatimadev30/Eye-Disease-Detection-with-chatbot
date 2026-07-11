import bcrypt
import streamlit as st
import sys
import os

# Add parent directory to path to allow importing from db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_connection

#Password Encryption aur Verification (
def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# User Registration and Authentication
def register_user(username: str, email: str, password: str, role: str = 'user', name: str = None) -> bool:
    """Registers a new user in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, role, name) VALUES (?, ?, ?, ?, ?)',
            (username, email, hashed_pw, role, name)
        )
        conn.commit()
        return True
    except Exception as e:
        # e.g., username or email already exists
        return False
    finally:
        conn.close()

#User Authentication
def authenticate_user(username: str, password: str) -> dict:
    """Authenticates a user and returns user info if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

#Session State Initialization 
    if user and verify_password(password, user['password_hash']):
        if user['is_active'] == 1:
            return dict(user)
        else:
            return {'error': 'Account deactivated.'}
    return None

def init_session_state():
    """Initializes Streamlit session state for authentication."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None

# LOGIN SESSION MANAGEMENT
def login(user_data: dict):
    """Logs the user in by updating session state."""
    st.session_state.logged_in = True
    st.session_state.user_id = user_data['id']
    st.session_state.username = user_data['username']
    st.session_state.role = user_data['role']
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        action_text = f"{'Admin' if user_data['role'] == 'admin' else 'User'} Login"
        cursor.execute(
            "INSERT INTO audit_logs (admin_id, action, target_user_id) VALUES (?, ?, ?)",
            (user_data['id'], action_text, user_data['id'])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging login: {e}")

# LOGOUT SESSION MANAGEMENT
def logout():
    """Logs the user out by clearing session state."""
    if st.session_state.get('user_id'):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            role_label = 'Admin' if st.session_state.get('role') == 'admin' else 'User'
            action_text = f"{role_label} Logout"
            cursor.execute(
                "INSERT INTO audit_logs (admin_id, action, target_user_id) VALUES (?, ?, ?)",
                (st.session_state.user_id, action_text, st.session_state.user_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging logout: {e}")

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
