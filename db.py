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

# --- Department Operations ---

def get_departments():
    """Fetch all departments."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments")
    depts = cursor.fetchall()
    conn.close()
    return depts

def add_department(name, hod=""):
    """Add a new department."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO departments (name, hod) VALUES (?, ?)", (name, hod))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- Student Operations ---

def add_student(data):
    """Add a new student. data should be a tuple of all student fields."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO students (roll_no, name, email, phone, dob, gender, address, dept_id, semester)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError as e:
        return False, f"Error: Roll Number or Email already exists."
    finally:
        conn.close()

def get_all_students():
    """Fetch all students with department name."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, d.name as dept_name 
        FROM students s 
        LEFT JOIN departments d ON s.dept_id = d.id
    ''')
    students = cursor.fetchall()
    conn.close()
    return students

def delete_student(roll_no):
    """Delete a student by roll number."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
    conn.commit()
    conn.close()
    return True

def search_students(query):
    """Search students by name or roll number."""
    conn = connect_db()
    cursor = conn.cursor()
    search_query = f"%{query}%"
    cursor.execute('''
        SELECT s.*, d.name as dept_name 
        FROM students s 
        LEFT JOIN departments d ON s.dept_id = d.id
        WHERE s.name LIKE ? OR s.roll_no LIKE ?
    ''', (search_query, search_query))
    results = cursor.fetchall()
    conn.close()
    return results

# --- Attendance Operations ---

def mark_attendance(student_id, date, status):
    """Mark a student as present or absent."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendance (student_id, date, status) 
        VALUES (?, ?, ?)
    ''', (student_id, date, status))
    conn.commit()
    conn.close()
    return True

def get_student_attendance(student_id):
    """Get attendance report for a specific student."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC", (student_id,))
    report = cursor.fetchall()
    conn.close()
    return report

# --- Marks Operations ---

def add_marks(student_id, subject, marks, max_marks=100):
    """Save or update marks for a student."""
    conn = connect_db()
    cursor = conn.cursor()
    # Check if marks already exist for this subject
    cursor.execute("SELECT id FROM marks WHERE student_id = ? AND subject = ?", (student_id, subject))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("UPDATE marks SET marks_obtained = ? WHERE id = ?", (marks, existing['id']))
    else:
        cursor.execute("INSERT INTO marks (student_id, subject, marks_obtained, max_marks) VALUES (?, ?, ?, ?)",
                       (student_id, subject, marks, max_marks))
    conn.commit()
    conn.close()
    return True

def get_student_marks(student_id):
    """Fetch all subject marks for a student."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM marks WHERE student_id = ?", (student_id,))
    marks = cursor.fetchall()
    conn.close()
    return marks

if __name__ == "__main__":
    initialize_db()
    # Add default depts if empty
    if not get_departments():
        add_department("Computer Science", "Dr. Smith")
        add_department("Information Technology", "Prof. Doe")
        add_department("Business Administration", "Dr. Brown")
