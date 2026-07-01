from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "asms_secret_key"

# ======================
# DATABASE CONFIG
# ======================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'asms_user'
app.config['MYSQL_PASSWORD'] = 'asms123'
app.config['MYSQL_DB'] = 'asms'

mysql = MySQL(app)

# ======================
# HOME
# ======================
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "All fields required", 400

        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO users(username, password, role)
            VALUES(%s, %s, %s)
        """, (username, hashed_password, 'teacher'))

        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

# ======================
# LOGIN
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):

            session['loggedin'] = True
            session['username'] = user[1]
            session['role'] = user[3]

            return redirect('/dashboard')

        return "Invalid login"

    return render_template('login.html')


# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ======================
# DASHBOARD
# ======================
@app.route('/dashboard')
def dashboard():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM teachers")
    teachers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM exams")
    exams = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM results")
    results = cur.fetchone()[0]

    cur.close()

    return render_template('dashboard.html',
        username=session['username'],
        students=students,
        teachers=teachers,
        exams=exams,
        results=results
    )


# ======================
# ADMIN
# ======================
@app.route('/admin')
def admin():

    if 'loggedin' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return "Access Denied", 403

    return render_template('admin.html',
        username=session['username']
    )


# ======================
# STUDENTS
# ======================
@app.route('/students')
def students():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()

    return render_template('students.html', students=data)


@app.route('/add_student', methods=['GET','POST'])
def add_student():

    if 'loggedin' not in session:
        return redirect('/login')

    if request.method == 'POST':

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO students(name, gender, class, age, parent_contact)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            request.form['name'],
            request.form['gender'],
            request.form['class'],
            request.form['age'],
            request.form['parent_contact']
        ))
        mysql.connection.commit()
        cur.close()

        return redirect('/students')

    return render_template('add_student.html')


@app.route('/edit_student/<int:id>', methods=['GET','POST'])
def edit_student(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        cur.execute("""
            UPDATE students SET name=%s, gender=%s, class=%s, age=%s, parent_contact=%s
            WHERE id=%s
        """, (
            request.form['name'],
            request.form['gender'],
            request.form['class'],
            request.form['age'],
            request.form['parent_contact'],
            id
        ))

        mysql.connection.commit()
        cur.close()

        return redirect('/students')

    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cur.fetchone()
    cur.close()

    return render_template('edit_student.html', student=student)


@app.route('/delete_student/<int:id>')
def delete_student(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect('/students')


# ======================
# TEACHERS
# ======================
@app.route('/teachers')
def teachers():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM teachers")
    data = cur.fetchall()
    cur.close()

    return render_template('teachers.html', teachers=data)


@app.route('/add_teacher', methods=['GET','POST'])
def add_teacher():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        cur.execute("""
            INSERT INTO teachers(fullname, gender, subject, phone, email)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            request.form['fullname'],
            request.form['gender'],
            request.form['subject'],
            request.form['phone'],
            request.form['email']
        ))

        mysql.connection.commit()
        cur.close()

        return redirect('/teachers')

    return render_template('add_teacher.html')


@app.route('/edit_teacher/<int:id>', methods=['GET','POST'])
def edit_teacher(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        cur.execute("""
            UPDATE teachers SET fullname=%s, gender=%s, subject=%s, phone=%s, email=%s
            WHERE id=%s
        """, (
            request.form['fullname'],
            request.form['gender'],
            request.form['subject'],
            request.form['phone'],
            request.form['email'],
            id
        ))

        mysql.connection.commit()
        cur.close()

        return redirect('/teachers')

    cur.execute("SELECT * FROM teachers WHERE id=%s", (id,))
    teacher = cur.fetchone()
    cur.close()

    return render_template('edit_teacher.html', teacher=teacher)


@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM teachers WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect('/teachers')


# ======================
# EXAMS
# ======================
@app.route('/exams')
def exams():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM exams")
    data = cur.fetchall()
    cur.close()

    return render_template('exams.html', exams=data)


@app.route('/add_exam', methods=['GET','POST'])
def add_exam():

    if 'loggedin' not in session:
        return redirect('/login')

    if request.method == 'POST':

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO exams(exam_name, exam_date, class_name)
            VALUES(%s,%s,%s)
        """, (
            request.form['exam_name'],
            request.form['exam_date'],
            request.form['class_name']
        ))
        mysql.connection.commit()
        cur.close()

        return redirect('/exams')

    return render_template('add_exam.html')


@app.route('/edit_exam/<int:id>', methods=['GET','POST'])
def edit_exam(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        cur.execute("""
            UPDATE exams SET exam_name=%s, exam_date=%s, class_name=%s
            WHERE id=%s
        """, (
            request.form['exam_name'],
            request.form['exam_date'],
            request.form['class_name'],
            id
        ))

        mysql.connection.commit()
        cur.close()

        return redirect('/exams')

    cur.execute("SELECT * FROM exams WHERE id=%s", (id,))
    exam = cur.fetchone()
    cur.close()

    return render_template('edit_exam.html', exam=exam)


@app.route('/delete_exam/<int:id>')
def delete_exam(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM exams WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect('/exams')


# ======================
# RESULTS SECTION
# ======================

@app.route('/results')
def results():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT results.id, students.name, exams.exam_name,
               results.subject, results.marks, results.grade
        FROM results
        JOIN students ON results.student_id = students.id
        JOIN exams ON results.exam_id = exams.id
    """)

    data = cur.fetchall()
    cur.close()

    return render_template('results.html', results=data)


# ======================
# ADD RESULT
# ======================
@app.route('/add_result', methods=['GET', 'POST'])
def add_result():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        student_id = request.form['student_id']
        exam_id = request.form['exam_id']
        subject = request.form['subject']
        marks = int(request.form['marks'])

        # grading
        if marks >= 80:
            grade = 'A'
        elif marks >= 60:
            grade = 'B'
        elif marks >= 40:
            grade = 'C'
        else:
            grade = 'F'

        cur.execute("""
            INSERT INTO results(student_id, exam_id, subject, marks, grade)
            VALUES(%s,%s,%s,%s,%s)
        """, (student_id, exam_id, subject, marks, grade))

        mysql.connection.commit()
        cur.close()

        return redirect('/results')

    # dropdown data
    cur.execute("SELECT id, name FROM students")
    students = cur.fetchall()

    cur.execute("SELECT id, exam_name FROM exams")
    exams = cur.fetchall()

    cur.close()

    return render_template('add_result.html',
                           students=students,
                           exams=exams)


# ======================
# EDIT RESULT
# ======================
@app.route('/edit_result/<int:id>', methods=['GET', 'POST'])
def edit_result(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        student_id = request.form.get('student_id')
        exam_id = request.form.get('exam_id')
        subject = request.form.get('subject')
        marks = request.form.get('marks')

        if not student_id or not exam_id or not subject or not marks:
            cur.close()
            return "Error: All fields are required.", 400

        marks = int(marks)

        if marks >= 80:
            grade = 'A'
        elif marks >= 60:
            grade = 'B'
        elif marks >= 40:
            grade = 'C'
        else:
            grade = 'F'

        cur.execute("""
            UPDATE results
            SET student_id=%s,
                exam_id=%s,
                subject=%s,
                marks=%s,
                grade=%s
            WHERE id=%s
        """, (student_id, exam_id, subject, marks, grade, id))

        mysql.connection.commit()
        return redirect('/results')

    cur.execute("SELECT * FROM results WHERE id=%s", (id,))
    result = cur.fetchone()

    cur.execute("SELECT id, name FROM students")
    students = cur.fetchall()

    cur.execute("SELECT id, exam_name FROM exams")
    exams = cur.fetchall()

    cur.close()

    return render_template(
        'edit_result.html',
        result=result,
        students=students,
        exams=exams
    )
# ======================
# DELETE RESULT
# ======================
@app.route('/delete_result/<int:id>')
def delete_result(id):

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM results WHERE id=%s", (id,))

    mysql.connection.commit()
    cur.close()

    return redirect('/results')

# ======================
# ANALYTICS
# ======================
@app.route('/results_analytics')
def results_analytics():

    if 'loggedin' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM results WHERE grade='A'")
    a = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM results WHERE grade='B'")
    b = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM results WHERE grade='C'")
    c = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM results WHERE grade='F'")
    f = cur.fetchone()[0]

    cur.close()

    return render_template('results_analytics.html',
        grade_a=a,
        grade_b=b,
        grade_c=c,
        grade_f=f
    )


# ======================
# SEARCH RESULTS
# ======================
@app.route('/search_results', methods=['GET','POST'])
def search_results():

    if 'loggedin' not in session:
        return redirect('/login')

    results = []

    if request.method == 'POST':

        keyword = request.form['keyword']

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT results.id, students.name, exams.exam_name,
                   results.subject, results.marks, results.grade
            FROM results
            JOIN students ON results.student_id = students.id
            JOIN exams ON results.exam_id = exams.id
            WHERE students.name LIKE %s
            OR exams.exam_name LIKE %s
            OR results.subject LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

        results = cur.fetchall()
        cur.close()

    return render_template('search_results.html', results=results)


# ======================
# RUN APP
# ======================
if __name__ == '__main__':
    app.run(debug=True)
