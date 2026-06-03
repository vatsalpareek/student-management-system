import sqlite3
import hashlib
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Database path - Use a user-writable folder (Home directory)
HOME_DIR = os.path.expanduser("~")
DB_DIR = os.path.join(HOME_DIR, "StudentManagementDB")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = os.path.join(DB_DIR, "student_system.db")

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

    # Migrate users table if columns are missing (Backward Compatibility)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN security_question TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN security_answer TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

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
    """Search students by name, roll number, email, phone, semester, or department name."""
    conn = connect_db()
    cursor = conn.cursor()
    search_query = f"%{query}%"
    cursor.execute('''
        SELECT s.*, d.name as dept_name 
        FROM students s 
        LEFT JOIN departments d ON s.dept_id = d.id
        WHERE s.name LIKE ? 
           OR s.roll_no LIKE ? 
           OR s.email LIKE ? 
           OR s.phone LIKE ? 
           OR s.semester LIKE ? 
           OR d.name LIKE ?
    ''', (search_query, search_query, search_query, search_query, search_query, search_query))
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

def update_marks(student_id, original_subject, new_subject, marks, max_marks=100):
    """Update a student's marks for a specific subject, allowing changing the subject name."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Check if they are renaming to an already existing subject for this student (other than the original one)
        if original_subject != new_subject:
            cursor.execute("SELECT id FROM marks WHERE student_id = ? AND subject = ?", (student_id, new_subject))
            if cursor.fetchone():
                return False, f"Marks already exist for subject '{new_subject}'."
                
        cursor.execute('''
            UPDATE marks 
            SET subject = ?, marks_obtained = ?, max_marks = ?
            WHERE student_id = ? AND subject = ?
        ''', (new_subject, marks, max_marks, student_id, original_subject))
        conn.commit()
        return True, "Marks updated successfully!"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def delete_marks(student_id, subject):
    """Delete a student's marks for a specific subject."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            DELETE FROM marks 
            WHERE student_id = ? AND subject = ?
        ''', (student_id, subject))
        conn.commit()
        return True, "Marks deleted successfully!"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

# --- Analytics & Reports ---

def get_stats():
    """Fetch general statistics for the dashboard."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM departments")
    total_depts = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(marks_obtained) FROM marks")
    avg_marks = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        "students": total_students,
        "depts": total_depts,
        "avg_marks": f"{avg_marks:.1f}%"
    }

def get_top_students(limit=5):
    """Fetch students with highest average marks."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.name, AVG(m.marks_obtained) as avg_score
        FROM students s
        JOIN marks m ON s.roll_no = m.student_id
        GROUP BY s.roll_no
        ORDER BY avg_score DESC
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_attendance_alerts(threshold=75):
    """Fetch students with attendance below threshold."""
    # This is a simplified calculation: (Present / Total Days) * 100
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.name, 
               (COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0 / COUNT(a.id)) as perc
        FROM students s
        JOIN attendance a ON s.roll_no = a.student_id
        GROUP BY s.roll_no
        HAVING perc < ?
    ''', (threshold,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_student(roll_no):
    """Fetch a student by roll number with department name."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, d.name as dept_name 
        FROM students s 
        LEFT JOIN departments d ON s.dept_id = d.id
        WHERE s.roll_no = ?
    ''', (roll_no,))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student(roll_no, data):
    """Update student details in the database. data should be a tuple (name, email, phone, dob, gender, address, dept_id, semester)"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        UPDATE students 
        SET name = ?, email = ?, phone = ?, dob = ?, gender = ?, address = ?, dept_id = ?, semester = ?
        WHERE roll_no = ?
        ''', data + (roll_no,))
        conn.commit()
        return True, "Student updated successfully!"
    except sqlite3.IntegrityError as e:
        return False, f"Error: Email already exists for another student."
    except sqlite3.Error as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def register_user(username, password, full_name, email, security_question, security_answer):
    """Register a new admin user."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists!"
        
    # Check if email already exists if provided
    if email:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already exists!"
            
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    hashed_ans = hashlib.sha256(security_answer.strip().lower().encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, security_question, security_answer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed_pw, full_name, email, security_question, hashed_ans))
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.Error as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_user_security_question(username):
    """Retrieve security question for a username."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT security_question FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['security_question']
    return None

def reset_password(username, security_answer, new_password):
    """Reset user password if security answer is correct."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT security_answer FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "User not found!"
        
    stored_answer = row['security_answer']
    if not stored_answer:
        conn.close()
        return False, "No security question configured for this account."
        
    hashed_ans = hashlib.sha256(security_answer.strip().lower().encode()).hexdigest()
    if hashed_ans != stored_answer:
        conn.close()
        return False, "Incorrect answer to security question."
        
    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, username))
    conn.commit()
    conn.close()
    return True, "Password reset successfully!"

def retrieve_username_by_email(email):
    """Retrieve username associated with an email address."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['username']
    return None

def backup_db(dest_path):
    """Create a backup of the database file."""
    import shutil
    try:
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))
        shutil.copy2(DB_PATH, dest_path)
        return True
    except Exception as e:
        print(f"Backup error: {e}")
        return False

if __name__ == "__main__":
    initialize_db()
    # Add default depts if empty
    if not get_departments():
        add_department("Computer Science", "Dr. Smith")
        add_department("Information Technology", "Prof. Doe")
        add_department("Business Administration", "Dr. Brown")
