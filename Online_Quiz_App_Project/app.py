from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'

# Connect to DB
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home/Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == 'admin' and pwd == 'admin':
            session['user'] = 'admin'
            return redirect('/admin')
        elif user == 'user' and pwd == 'user':
            session['user'] = 'user'
            session['score'] = 0
            return redirect('/quiz')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

# Quiz Page
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user' not in session or session['user'] != 'user':
        return redirect('/')
    
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()
    
    if request.method == 'POST':
        selected = request.form['answer']
        correct = request.form['correct']
        if selected == correct:
            session['score'] += 1
    
    index = int(request.args.get('q', 0))
    if index >= len(questions):
        return redirect('/result')
    
    question = questions[index]
    return render_template('quiz.html', question=question, index=index, total=len(questions))

# Results
@app.route('/result')
def result():
    score = session.get('score', 0)
    return render_template('result.html', score=score)

# Admin Panel
@app.route('/admin')
def admin():
    if 'user' not in session or session['user'] != 'admin':
        return redirect('/')
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()
    return render_template('admin.html', questions=questions)

# Add Question
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        question = request.form['question']
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        d = request.form['d']
        correct = request.form['correct']
        conn = get_db_connection()
        conn.execute("INSERT INTO questions (question, a, b, c, d, correct) VALUES (?, ?, ?, ?, ?, ?)",
                     (question, a, b, c, d, correct))
        conn.commit()
        conn.close()
        return redirect('/admin')
    return render_template('add_question.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
