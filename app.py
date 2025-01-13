import os
from cs50 import SQL
from flask import Flask, render_template, session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
from help import login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = SQL("sqlite:///tigrinho.db")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Limpar os dados da sessão anterior
    session.clear()
    #Checar se é POST
    if request.method == 'POST':
    #Pegar o username e senha
       username = request.form.get('username')
       password = request.form.get('password')
       #checar se usuario colocou username ou senha
       if not username or not password:
        return "Preencha todos os campos!", 400
       #Obter usuario no db
       user = db.execute("SELECT * FROM users WHERE username = ?", username)
       #Verificar se usuario existe e se a senha esta correta
       if len(user) != 1 or not check_password_hash(user[0]['password'], password):
            return "Usuário ou senha inválidos!", 400
       #redirecionar usuario
       session['user_id'] = user[0]['id']
       return redirect(url_for('index'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    #Esquecer o id do usuario
    session.clear()
    # Voltar o usuario para tela inicial
    return redirect(url_for('index'))

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
        db.execute("INSERT INTO users (username, password, saldo) VALUES(?, ?, ?)", username, hashed_password, 100)
        return redirect(url_for('login'))
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)