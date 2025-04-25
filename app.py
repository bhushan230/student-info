from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Database connection
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Replace with your MySQL password
        database='student_dashboard'
    )

@app.route('/', methods=['GET'])
def search():
    return render_template('search.html')

@app.route('/login', methods=['POST'])
def login():
    roll_no = request.form['roll_no']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE student_id = %s", (roll_no,))
    student_info = cursor.fetchone()

    cursor.close()
    conn.close()

    if student_info and student_info['password'] == password:
        return redirect(url_for('student_dashboard', student_id=student_info['student_id']))
    else:
        return "Invalid roll number or password", 401

@app.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    student_id = request.args.get('student_id')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student_info = cursor.fetchone()

    if not student_info:
        return "Student not found", 404

    # ✅ Handle Photo URL
    photo_filename = student_info.get('photo_filename') or 'default.jpg'
    student_info['photo_url'] = url_for('static', filename=f'uploads/{photo_filename}')

    # ✅ CT1 Marks
    cursor.execute("SELECT * FROM ct1_marks WHERE student_id = %s", (student_id,))
    ct1_data = cursor.fetchone()
    ct1_marks = [
        {'marks': ct1_data.get('subject_1_marks') if ct1_data and ct1_data.get('subject_1_marks') is not None else '-'},
        {'marks': ct1_data.get('subject_2_marks') if ct1_data and ct1_data.get('subject_2_marks') is not None else '-'},
        {'marks': ct1_data.get('subject_3_marks') if ct1_data and ct1_data.get('subject_3_marks') is not None else '-'},
        {'marks': ct1_data.get('subject_4_marks') if ct1_data and ct1_data.get('subject_4_marks') is not None else '-'},
    ]
    ct1_total = ct1_data.get('total') if ct1_data and ct1_data.get('total') is not None else '-'

    # ✅ CT2 Marks
    cursor.execute("SELECT * FROM ct2_marks WHERE student_id = %s", (student_id,))
    ct2_data = cursor.fetchone()
    ct2_marks = [
        {'marks': ct2_data.get('subject_1_marks') if ct2_data and ct2_data.get('subject_1_marks') is not None else '-'},
        {'marks': ct2_data.get('subject_2_marks') if ct2_data and ct2_data.get('subject_2_marks') is not None else '-'},
        {'marks': ct2_data.get('subject_3_marks') if ct2_data and ct2_data.get('subject_3_marks') is not None else '-'},
        {'marks': ct2_data.get('subject_4_marks') if ct2_data and ct2_data.get('subject_4_marks') is not None else '-'},
    ]
    ct2_total = ct2_data.get('total') if ct2_data and ct2_data.get('total') is not None else '-'

    # ✅ Semester Marks
    cursor.execute("SELECT * FROM semester_marks WHERE student_id = %s", (student_id,))
    semester_data = cursor.fetchone()
    semester_marks = [
        {'marks': semester_data.get(f'subject_{i}_marks') if semester_data and semester_data.get(f'subject_{i}_marks') is not None else '-'}
        for i in range(1, 11)
    ]
    semester_total = semester_data.get('total') if semester_data and semester_data.get('total') is not None else '-'

    # ✅ Leave History
    cursor.execute("SELECT leave_date, reason FROM leave_history WHERE student_id = %s", (student_id,))
    leave_history = cursor.fetchall() or []

    cursor.close()
    conn.close()

    return render_template(
        'student_dashboard.html',
        student_info=student_info,
        ct1_marks=ct1_marks,
        ct1_total=ct1_total,
        ct2_marks=ct2_marks,
        ct2_total=ct2_total,
        semester_marks=semester_marks,
        semester_total=semester_total,
        leave_history=leave_history,
        attendance={'attendance_percentage': student_info.get('attendance_percentage', 0)}
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use platform's assigned port
    app.run(debug=False, host="0.0.0.0", port=port)
