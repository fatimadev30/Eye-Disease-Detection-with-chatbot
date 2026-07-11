import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth.security import register_user
from db.database import init_db

init_db()

print("--- Create Admin User ---")
username = input("Enter admin username: ")
email = input("Enter admin email: ")
password = input("Enter admin password: ")

success = register_user(username, email, password, role='admin')
if success:
    print(f"Success! Admin user '{username}' has been created.")
else:
    print("Error: Username or email already exists.")
