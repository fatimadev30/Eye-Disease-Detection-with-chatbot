import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edd.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# delete prediction and upload
def delete_prediction(prediction_id):
    """Deletes a prediction record and its associated upload entry."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get upload_id first
        cursor.execute("SELECT upload_id FROM predictions WHERE id = ?", (prediction_id,))
        res = cursor.fetchone()
        if res:
            upload_id = res['upload_id']
            # Delete prediction
            cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
            # Delete upload
            cursor.execute("DELETE FROM uploads WHERE id = ?", (upload_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return False
    finally:
        conn.close()
    return False

               # chat save 

def save_chat_message(user_id, role, message, prediction_id=None):
    """Saves a chat message to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO chat_history (user_id, role, message, prediction_id)
            VALUES (?, ?, ?, ?)
        ''', (user_id, role, message, prediction_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving chat message: {e}")
        return False
    finally:
        conn.close()

                       # chat history get

def get_chat_history(user_id, prediction_id=None):
    """Retrieves chat history for a user, optionally filtered by prediction_id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if prediction_id:
            cursor.execute('''
                SELECT role, message, timestamp 
                FROM chat_history 
                WHERE user_id = ? AND prediction_id = ? 
                ORDER BY timestamp ASC
            ''', (user_id, prediction_id))
        else:
            cursor.execute('''
                SELECT role, message, timestamp 
                FROM chat_history 
                WHERE user_id = ? AND prediction_id IS NULL 
                ORDER BY timestamp ASC
            ''', (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return []
    finally:
        conn.close()

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure 'name' column exists in case database was already created
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists


    # Create uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            predicted_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities_json TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (upload_id) REFERENCES uploads (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create audit_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_user_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users (id),
            FOREIGN KEY (target_user_id) REFERENCES users (id)
        )
    ''')

    # Create chat_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prediction_id INTEGER,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (prediction_id) REFERENCES predictions (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
