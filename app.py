import os
from cs50 import SQL
from flask import Flask, render_template, session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
from help import login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = SQL("sqlite:///tigrinho.db")

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
   #Limpar a sessao anterior
    session.clear()

    if request.method == "POST":
        #Obter os dados
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        #Checar se usuario prencheu todos os campos
        if not username or not password or not confirm:
            return "Preencha todos os campos", 400
        #checar se senha = confirmação
        if password != confirm:
            return "Confirmação precisa ser igual a senha!", 400
        #Codificar a senha
        hashed_password = generate_password_hash(password)
        #Verificar se usuario ja existe
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if user:
            return "O nome ja foi selecionado", 400
        #Adicionar dados para db
        db.execute("INSERT INTO users (username, password) VALUES(?, ?)", username, hashed_password)
        return redirect(url_for('login'))
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)