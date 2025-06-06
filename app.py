from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"
DATABASE = 'bus_log.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/bus/<bus_id>')
def bus_view(bus_id):
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students WHERE bus = ?', (bus_id,)).fetchall()
    checked_in = sum(1 for s in students if s['status'] == 'checked_in')
    not_checked_in = sum(1 for s in students if s['status'] == 'not_checked_in')
    conn.close()

    ordered = sorted(
        students,
        key=lambda x: {'checked_in': 0, 'not_checked_in': 1, 'not_coming': 2}.get(x['status'], 3)
    )
    return render_template('bus_page.html', students=ordered, bus=bus_id,
                           checked_in=checked_in, not_checked_in=not_checked_in)


@app.route('/all_buses')
def all_buses():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    bus_summary = {}
    for s in students:
        if s['status'] == 'not_coming':
            continue
        bus = s['bus']
        if bus not in bus_summary:
            bus_summary[bus] = {'checked_in': 0, 'not_checked_in': 0}
        if s['status'] == 'checked_in':
            bus_summary[bus]['checked_in'] += 1
        elif s['status'] == 'not_checked_in':
            bus_summary[bus]['not_checked_in'] += 1
    conn.close()
    ordered = sorted(
        students,
        key=lambda x: (x['bus'], {'checked_in': 0, 'not_checked_in': 1, 'not_coming': 2}.get(x['status'], 3))
    )
    return render_template('all_buses.html', students=ordered, bus_summary=bus_summary)


@app.route('/log/<bus_id>', methods=['POST'])
def log_barcode(bus_id):
    barcode = request.form['barcode'].strip()
    conn = get_db_connection()
    c = conn.cursor()
    student = c.execute('SELECT * FROM students WHERE barcode = ?', (barcode,)).fetchone()

    if not student:
        students = c.execute('SELECT * FROM students WHERE bus = ?', (bus_id,)).fetchall()
        checked_in = sum(1 for s in students if s['status'] == 'checked_in')
        not_checked_in = sum(1 for s in students if s['status'] == 'not_checked_in')
        conn.close()
        return render_template('bus_page.html', students=students, bus=bus_id,
                               checked_in=checked_in, not_checked_in=not_checked_in,
                               error="❌ No student found.")

    c.execute('UPDATE students SET status = ? WHERE id = ?', ('checked_in', student['id']))
    c.execute('INSERT INTO logs (barcode, bus_number, timestamp) VALUES (?, ?, ?)',
              (barcode, student['bus'], datetime.now()))
    conn.commit()
    students = c.execute('SELECT * FROM students WHERE bus = ?', (bus_id,)).fetchall()
    checked_in = sum(1 for s in students if s['status'] == 'checked_in')
    not_checked_in = sum(1 for s in students if s['status'] == 'not_checked_in')
    conn.close()
    full_name = f"{student['first_name']} {student['last_name']}"
    bunk = student['bunk']
    return render_template('bus_page.html', students=students, bus=bus_id,
                           checked_in=checked_in, not_checked_in=not_checked_in,
                           success=f"✅ {full_name} in Bunk {bunk} was checked in.")


@app.route('/set_status/<student_id>/<status>', methods=['POST'])
def set_status(student_id, status):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if student:
        conn.execute('UPDATE students SET status = ? WHERE id = ?', (status, student_id))
        conn.commit()
    conn.close()
    return redirect(url_for('bus_view', bus_id=student['bus'] if student else ''))


if __name__ == '__main__':
    app.run(debug=True)
