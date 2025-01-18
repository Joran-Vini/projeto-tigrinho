import os
from cs50 import SQL
from flask import Flask, render_template, session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
import random
from help import login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = SQL("sqlite:///tigrinho.db")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/homepage', methods=['GET', 'POST'])
@login_required
def homepage():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
   # Obter o saldo e nome do usuário logado
    user = db.execute("SELECT username, saldo FROM users WHERE id = ?", user_id)
    if not user:
        return "Usuário não encontrado.", 404
    username = user[0]["username"]
    saldo = user[0]["saldo"]
    # Renderizar a página com o saldo
    return render_template('homepage.html',username=username, saldo=saldo)

@app.route('/niquel', methods=['GET', 'POST'])
@login_required
def niquel():
   user_id = session.get('user_id')
   saldo = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)[0]['saldo']
   if request.method == 'POST':
        if saldo < 10:
            return "Saldo não disponivel", 404        
       # Símbolos do caça-níqueis
        symbols = ["🍒", "🍋", "⭐", "🔔", "🍀"]
       # Gerar os três slots 
        grid = [[random.choice(symbols) for _ in range(3)] for _ in range(3)]
        #Checar resultado
        prize = 0
        for row in grid:
            if row.count(row[0]) == 3:  # Todos os símbolos na linha são iguais
                prize += 50
        if prize == 0:
                perda = 10
                saldo -= perda
                message = f"Você perdeu {perda} fichas."  
                message_class = "perdeu"
        else:
            saldo += prize
            message = f"Você ganhou {prize} fichas! Parabéns!"    
            message_class = "ganhou"
        db.execute("UPDATE users SET saldo = ? WHERE id = ?", saldo, user_id)
        return render_template('niquel.html', grid=grid, saldo=saldo, message=message, message_class=message_class)              
   return render_template("niquel.html", saldo=saldo)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    #Obter o id do usuario
    user_id = session.get('user_id')
    user = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)
    if not user:
        return "Usuário não encontrado.", 404
    saldo = user[0]["saldo"]
    if request.method == 'POST':
         #Obter a quantidade de fichas a serem adicionadas
        fichas = request.form.get('fichas')
        #Checar se é um valor possivel
        if not fichas or not fichas.isdigit() or int(fichas) <= 0:
            return "Por favor, insira um número válido de fichas.", 400
    #Atualizar o saldo
        db.execute("UPDATE users SET saldo = saldo + ? WHERE id = ?", int(fichas), user_id)
        #Redirecionar usuario para homepage
        return redirect(url_for('homepage'))
    return render_template("add.html", saldo=saldo)
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
       return redirect(url_for('homepage'))
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