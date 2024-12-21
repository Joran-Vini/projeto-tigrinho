from cs50 import SQL
from flask import Flask, render_template, session, redirect, url_for, request

from help import login_required

app = Flask(__name__)
app.secret_key = 'Chave secreta!'

@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_id'] = request.form['username']
        return redirect(url_for('dashboard'))
    else:
         return render_template("login.html")
