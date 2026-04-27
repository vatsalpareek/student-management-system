import sqlite3
import hashlib
import os

# Database path
DB_PATH = os.path.join("database", "student_system.db")

def connect_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def initialize_db():
    """Create tables if they don't exist."""
    print("Initializing database...")
    if not os.path.exists("database"):
        os.makedirs("database")
        
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Users Table (Admin)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        last_login DATETIME
    )
    ''')

    # 2. Departments Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        hod TEXT
    )
    ''')

    # 3. Students Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        dob DATE,
        gender TEXT,
        address TEXT,
        dept_id INTEGER,
        semester TEXT,
        FOREIGN KEY (dept_id) REFERENCES departments (id)
    )
    ''')

    # 4. Attendance Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        date DATE NOT NULL,
        status TEXT CHECK(status IN ('Present', 'Absent')),
        FOREIGN KEY (student_id) REFERENCES students (roll_no)
    )
    ''')

    # 5. Marks Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        subject TEXT NOT NULL,
        marks_obtained INTEGER,
        max_marks INTEGER DEFAULT 100,
        FOREIGN KEY (student_id) REFERENCES students (roll_no)
    )
    ''')

    # Create a default admin user if none exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)",
                       ("admin", hashed_pw, "System Administrator"))
        print("Default admin created: admin / admin123")

    conn.commit()
    conn.close()
    print("Database initialization complete.")

def authenticate(username, password):
    """Authenticate a user."""
    conn = connect_db()
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    return user

if __name__ == "__main__":
    initialize_db()
