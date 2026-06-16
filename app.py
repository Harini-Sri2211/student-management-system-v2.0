import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Create database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    ''')

    # Attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        status TEXT
    )
    ''')
    # Results table
    cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    subject TEXT,
    marks INTEGER
)
''')

    # Default users
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('student1', '123', 'student')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('24BCA001', 'pass001', 'student')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('24BCA002', 'pass002', 'student')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('24BCA003', 'pass003', 'student')")

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('login.html',error="")
@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=? AND role=?",
        (username, password, role)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        # Admin Login
        if role == "admin":

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM attendance")

            records = cursor.fetchall()

            conn.close()

            return render_template(
                'admin_dashboard.html',
                records=records
            )

        # Student Login
        else:

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Attendance
            cursor.execute(
                "SELECT date, status FROM attendance WHERE student_name=?",
                (username,)
            )

            attendance = cursor.fetchall()

            # Results
            cursor.execute(
                "SELECT subject, marks FROM results WHERE student_name=?",
                (username,)
            )

            results = cursor.fetchall()

            # Percentage Calculation
            total_marks = 0

            for row in results:
                total_marks += row[1]

            if len(results) > 0:
                percentage = total_marks / len(results)
            else:
                percentage = 0

            # Grade Calculation
            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            else:
                grade = "D"

            conn.close()

            return render_template(
                'student_dashboard.html',
                attendance=attendance,
                results=results,
                percentage=percentage,
                grade=grade
            )

    else:

        return render_template(
            'login.html',
            error="Invalid Username or Password"
        )
# Add attendance
@app.route('/add_attendance', methods=['POST'])
def add_attendance():

    student_name = request.form['student_name']
    date = request.form['date']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO attendance (student_name, date, status) VALUES (?, ?, ?)",
        (student_name, date, status)
    )

    conn.commit()
    conn.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")

    records = cursor.fetchall()

    conn.close()

    return render_template(
    'admin_dashboard.html',
    records=records
)
@app.route('/edit/<int:id>')
def edit_attendance(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM attendance WHERE id=?",
        (id,)
    )

    record = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_attendance.html',
        record=record
    )
@app.route('/update/<int:id>', methods=['POST'])
def update_attendance(id):

    student_name = request.form['student_name']
    date = request.form['date']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE attendance
        SET student_name=?, date=?, status=?
        WHERE id=?
        ''',
        (student_name, date, status, id)
    )

    conn.commit()

    cursor.execute("SELECT * FROM attendance")

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_dashboard.html',
        records=records
    )
@app.route('/delete/<int:id>')
def delete_attendance(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM attendance WHERE id=?",
        (id,)
    )

    conn.commit()

    cursor.execute("SELECT * FROM attendance")

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_dashboard.html',
        records=records
    )
@app.route('/results')
def results_page():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results")

    results = cursor.fetchall()

    conn.close()

    return render_template(
        'results.html',
        results=results
    )
@app.route('/add_result', methods=['POST'])
def add_result():

    student_name = request.form['student_name']
    subject = request.form['subject']
    marks = request.form['marks']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO results
        (student_name, subject, marks)
        VALUES (?, ?, ?)
        ''',
        (student_name, subject, marks)
    )

    conn.commit()

    cursor.execute("SELECT * FROM results")

    results = cursor.fetchall()

    return render_template(
        'results.html',
        results=results
    )


@app.route('/edit_result/<int:id>')
def edit_result(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM results WHERE id=?",
        (id,)
    )

    result = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_result.html',
        result=result
    )  
@app.route('/update_result/<int:id>', methods=['POST'])
def update_result(id):

    student_name = request.form['student_name']
    subject = request.form['subject']
    marks = request.form['marks']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE results
        SET student_name=?, subject=?, marks=?
        WHERE id=?
        ''',
        (student_name, subject, marks, id)
    )

    conn.commit()

    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()

    conn.close()

    return render_template(
        'results.html',
        results=results
    )
@app.route('/delete_result/<int:id>')
def delete_result(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM results WHERE id=?",
        (id,)
    )

    conn.commit()

    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()

    conn.close()

    return render_template(
        'results.html',
        results=results
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
  