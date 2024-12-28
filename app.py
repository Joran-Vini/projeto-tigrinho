import os
from cs50 import SQL
from flask import Flask, render_template, session, redirect, url_for, request
from help import login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
@login_required
def index():
    return render_template('layout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        session['user_id'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)