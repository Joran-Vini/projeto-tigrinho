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
   # Obter o saldo e nome do usuário logado
    user = db.execute("SELECT username, saldo FROM users WHERE id = ?", user_id)
    if not user:
        return "Usuário não encontrado.", 404
    username = user[0]["username"]
    saldo = user[0]["saldo"]
    # Renderizar a página com o saldo
    return render_template('homepage.html',username=username, saldo=saldo)

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [rank + suit for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def calculate_score(hand):
    #Calcula o valor total de uma mão no blackjack
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
    score = sum(values[card[:-1]] for card in hand)
    # Ajustar o valor do Ás se necessário
    ace_count = sum(1 for card in hand if card[:-1] == 'A')
    while score > 21 and ace_count > 0:
        score -= 10
        ace_count -= 1
    return score

# Registrar o filtro calculate_score no Jinja2
@app.template_filter('calculate_score')
def calculate_score_filter(hand):
    return calculate_score(hand)

@app.route('/blackjack', methods=['GET', 'POST'])
@login_required
def blackjack():
    # Inicializar o jogo
    user_id = session['user_id']
    saldo = db.execute("SELECT saldo from users WHERE id = ?", user_id)[0]['saldo']
    if request.method == 'GET' or 'deck' not in session:
        deck = create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        session['deck'] = deck
        session['player_hand'] = player_hand
        session['dealer_hand'] = dealer_hand
    else:
        deck = session['deck']
        player_hand = session['player_hand']
        dealer_hand = session['dealer_hand']
    # Jogador pediu uma carta
    if request.method == 'POST' and 'hit' in request.form:
        if saldo < 10:
            return "Saldo insuficiente", 404
        player_hand.append(deck.pop())
        session['player_hand'] = player_hand
        session['deck'] = deck
        if calculate_score(player_hand) > 21:
            perda = 10 
            saldo -= perda  
            message_class = "perdeu"
            db.execute("UPDATE users SET saldo = ?, perdas = perda + ? WHERE id = ?", saldo, perda, user_id)
            return render_template('blackjack.html', 
                                   player_hand=player_hand, 
                                   dealer_hand=dealer_hand, 
                                   message="Você estourou! Fim de jogo.", 
                                   game_over=True, saldo=saldo, message_class=message_class)
    # Jogador decidiu parar
    if request.method == 'POST' and 'stand' in request.form:
        if saldo < 10:
            return "Saldo insuficiente", 404
        while calculate_score(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
        session['dealer_hand'] = dealer_hand
        player_score = calculate_score(player_hand)
        dealer_score = calculate_score(dealer_hand)
        if dealer_score > 21 or player_score > dealer_score:
            message = "Você venceu!"
            ganho = 10
            saldo += ganho
            message_class = "ganhou"
            db.execute("UPDATE users SET ganhos = ? WHERE id = ?", ganho, user_id)
        elif player_score < dealer_score:
            message = "Você perdeu!"
            perda = 10
            saldo -= perda
            message_class = "perdeu"
            db.execute("UPDATE users SET perdas = ? WHERE id = ?", perda, user_id)
        else:
            message = "Empate!"
        db.execute("UPDATE users SET saldo = ? WHERE id = ?", saldo, user_id)    
        return render_template('blackjack.html', 
                               player_hand=player_hand, 
                               dealer_hand=dealer_hand, 
                               message=message, 
                               game_over=True,saldo=saldo, message_class=message_class)
    return render_template('blackjack.html', 
                           player_hand=player_hand, 
                           dealer_hand=dealer_hand, 
                           game_over=False, saldo=saldo)
    
@app.route('/niquel', methods=['GET', 'POST'])
@login_required
def niquel():
   # Símbolos do caça-níqueis
   symbols = ["🍒", "🍋", "⭐", "🔔", "🍀", "💎", "🍊"]
   user_id = session.get('user_id')
   saldo = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)[0]['saldo']
   # Gerar os três slots 
   grid = [[random.choice(symbols) for _ in range(3)] for _ in range(3)]
   if request.method == 'POST':
        if saldo < 10:
            return "Saldo não disponivel", 404        
       # Gerar os três slots 
        grid = [[random.choice(symbols) for _ in range(3)] for _ in range(3)]
        #Checar resultado
        prize = 0
        #Verificar Linhas
        for row in grid:
            if row.count(row[0]) == 3:  
                prize += 25
        # Verificar colunas
        for col in range(3):
            column = [grid[row][col] for row in range(3)]
            if len(set(column)) == 1:
                prize += 10        
        # Verificar diagonais
        diagonal1 = [grid[i][i] for i in range(3)]
        diagonal2 = [grid[i][2 - i] for i in range(3)]
        if len(set(diagonal1)) == 1:
            prize += 50
        if len(set(diagonal2)) == 1:
            prize += 100
            #Checar derrota
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
   return render_template("niquel.html", saldo=saldo, grid=grid)

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

@app.route("/historico")
@login_required
def historico():
    user_id = session.get('user_id')
    perdas = db.execute("SELECT perdas FROM users WHERE id = ?", user_id)[0]['perdas']
    ganhos = db.execute("SELECT ganhos FROM users WHERE id = ?", user_id)[0]['ganhos']

    return render_template("historico.html", perdas=perdas, ganhos=ganhos)


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