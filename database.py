import sqlite3
import hashlib

# Helper function to create a connection to SQLite
def get_connection():
    conn = sqlite3.connect('users_data.db')  # Database file
    return conn

# Create the users table
def create_users_table():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT
        );
    ''')
    conn.commit()
    conn.close()

# Hash password before storing it
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Save user to database
def save_user_to_db(username, email, password):
    conn = get_connection()
    hashed_password = hash_password(password)

    try:
        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # User already exists
    finally:
        conn.close()
    return True

# Check if a user exists
def is_user_exists(username=None, email=None):
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Validate login credentials
def validate_login(username_or_email, password):
    conn = get_connection()
    hashed_password = hash_password(password)
    cursor = conn.execute(
        "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
        (username_or_email, username_or_email, hashed_password)
    )
    user = cursor.fetchone()
    conn.close()
    return user

# Update user password
def update_user_password(identifier, new_password, by_email=False):
    conn = get_connection()
    hashed_password = hash_password(new_password)
    if by_email:
        conn.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, identifier))
    else:
        conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, identifier))
    conn.commit()
    conn.close()

# Ensure table is created
create_users_table()
