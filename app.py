from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor(dictionary=True)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return "Incorrect email or password."
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        user_id = session['user_id']
        cursor.execute("INSERT INTO feedbacks (user_id, title, description, category) VALUES (%s, %s, %s, %s)", (user_id, title, description, category))
        conn.commit()

    cursor.execute("SELECT * FROM feedbacks WHERE user_id = %s", (session['user_id'],))
    feedbacks = cursor.fetchall()
    return render_template('dashboard.html', feedbacks=feedbacks)

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        feedback_id = request.form['feedback_id']
        status = request.form['status']
        cursor.execute("UPDATE feedbacks SET status = %s WHERE feedback_id = %s", (status, feedback_id))
        conn.commit()

    cursor.execute("SELECT feedbacks.*, users.name FROM feedbacks JOIN users ON feedbacks.user_id = users.user_id")
    feedbacks = cursor.fetchall()
    return render_template('admin_panel.html', feedbacks=feedbacks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)