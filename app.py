import os
from cs50 import SQL
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
import random
from werkzeug.security import check_password_hash, generate_password_hash
from help import login_required, create_deck, calculate_score, calcular_premiacao

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = SQL("sqlite:///tigrinho.db")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/homepage')
@login_required
def homepage():
    user_id = session.get('user_id')
    user = db.execute("SELECT username, saldo FROM users WHERE id = ?", user_id)
    
    if not user:
        flash("Erro ao carregar perfil. Faça login novamente.", "danger")
        return redirect(url_for('logout'))
    
    return render_template('homepage.html', 
                         username=user[0]["username"], 
                         saldo=user[0]["saldo"])


# Registrar o filtro calculate_score no Jinja2
@app.template_filter('calculate_score')
def calculate_score_filter(hand):
    return calculate_score(hand)

@app.route('/blackjack', methods=['GET', 'POST'])
@login_required
def blackjack():
    user_id = session['user_id']
    username = db.execute("SELECT username from users WHERE id = ?", user_id)[0]['username']
    user = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)
    
    if not user:
        flash("Erro de sessão. Faça login novamente.", "danger")
        return redirect(url_for('login'))
    
    saldo = user[0]['saldo']

    # Resetar totalmente o jogo se for uma nova partida
    if request.method == 'GET' and 'reset' in request.args:
        session.pop('deck', None)
        session.pop('player_hand', None)
        session.pop('dealer_hand', None)
        session.pop('dealer_hidden', None)
        session.pop('current_bet', None)
        session.pop('game_over', None)
        return redirect(url_for('blackjack'))

    # Fase de APOSTA
    if request.method == 'POST' and 'place_bet' in request.form:
        try:
            current_bet = int(request.form.get('bet_amount'))
            if current_bet < 1 or current_bet > saldo:
                flash("Valor de aposta inválido!", "danger")
                return redirect(url_for('blackjack'))
            
            # Iniciar novo jogo com sessão limpa
            deck = create_deck()
            session.update({
                'deck': deck,
                'player_hand': [deck.pop(), deck.pop()],
                'dealer_hand': [deck.pop()],  # 1 carta visível
                'dealer_hidden': deck.pop(),  # 1 carta escondida
                'current_bet': current_bet,
                'game_over': False
            })
            return redirect(url_for('blackjack'))

        except ValueError:
            flash("Digite um número válido!", "danger")
            return redirect(url_for('blackjack'))

    # Fase de JOGO (Hit/Stand)
    elif request.method == 'POST' and session.get('current_bet'):
        deck = session['deck']
        player_hand = session['player_hand']
        dealer_hand = session['dealer_hand']
        current_bet = session['current_bet']

        if 'hit' in request.form:
            player_hand.append(deck.pop())
            session['player_hand'] = player_hand
            
            if calculate_score(player_hand) > 21:
                # Revelar carta escondida e finalizar
                dealer_hand.append(session['dealer_hidden'])
                db.execute("UPDATE users SET saldo = saldo - ?, perdas = perdas + ? WHERE id = ?", 
                          current_bet, current_bet, user_id)
                session.update({
                    'game_over': True,
                    'dealer_hand': dealer_hand,
                    'result_message': f"Estourou! Perdeu {current_bet} fichas",
                    'message_class': "danger"
                })

        elif 'stand' in request.form:
            # Revelar carta escondida e jogar dealer
            dealer_hand.append(session['dealer_hidden'])
            while calculate_score(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
            
            player_score = calculate_score(player_hand)
            dealer_score = calculate_score(dealer_hand)
            
            if dealer_score > 21 or player_score > dealer_score:
                db.execute("UPDATE users SET saldo = saldo + ?, ganhos = ganhos + ? WHERE id = ?", 
                          current_bet, current_bet, user_id)
                result_message = f"Vitória! Ganhou {current_bet} fichas"
                message_class = "success"
            elif player_score < dealer_score:
                db.execute("UPDATE users SET saldo = saldo - ?, perdas = perdas + ? WHERE id = ?", 
                          current_bet, current_bet, user_id)
                result_message = f"Derrota! Perdeu {current_bet} fichas"
                message_class = "danger"
            else:
                result_message = "Empate! Fichas devolvidas"
                message_class = "warning"

            session.update({
                'game_over': True,
                'dealer_hand': dealer_hand,
                'result_message': result_message,
                'message_class': message_class
            })

        return redirect(url_for('blackjack'))

    # Atualizar saldo após operações
    saldo = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)[0]['saldo']

    return render_template('blackjack.html',
                         saldo=saldo, username=username,
                         game_over=session.get('game_over'),
                         player_hand=session.get('player_hand'),
                         dealer_hand=session.get('dealer_hand'),
                         current_bet=session.get('current_bet'),
                         result_message=session.get('result_message'),
                         message_class=session.get('message_class'))

@app.route('/roleta', methods=['GET', 'POST'])
@login_required
def roleta():
    user_id = session.get('user_id')
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    username = db.execute("SELECT username from users WHERE id = ?", user_id)[0]['username']
    saldo = user['saldo']

    if request.method == 'POST':
        # Obter dados da aposta
        tipo_aposta = request.form.get('tipo_aposta')
        aposta = request.form.get('aposta')
        valor_apostado = int(request.form.get('valor_apostado'))

        # Validações básicas
        if valor_apostado > saldo:
            return jsonify({
                "success": False,
                "mensagem": "Saldo insuficiente."
            }), 400

        # Gerar resultado (0-15)
        numero_sorteado = random.randint(0, 15)
        if numero_sorteado in [0, 15]:
            cor_resultado = 'green'
        else:
            cor_resultado = 'vermelho' if numero_sorteado % 2 == 1 else 'preto' 
        # Adicione esta linha para debug:
        print(f"DEBUG: Número sorteado: {numero_sorteado}, Cor: {cor_resultado}") 
        # Lógica de apostas atualizada
        ganho = 0
        if tipo_aposta == "numero":
            if aposta.isdigit() and int(aposta) == numero_sorteado:
                ganho = valor_apostado * 15  # Multiplicador do Double
        elif tipo_aposta == "cor":
            if aposta.lower() == cor_resultado:
                if aposta.lower() == 'verde':
                    ganho = valor_apostado * 5
                else:     
                    ganho = valor_apostado * 2
        elif tipo_aposta == "par_impar":
            if (numero_sorteado % 2 == 0 and aposta.lower() == "par") or \
               (numero_sorteado % 2 == 1 and aposta.lower() == "ímpar"):
                ganho = valor_apostado * 2
        elif tipo_aposta == "baixo_alto":
            if (0 <= numero_sorteado <= 7 and aposta.lower() == "baixo") or \
               (8 <= numero_sorteado <= 15 and aposta.lower() == "alto"):
                ganho = valor_apostado * 2
        # Atualizar saldo
        saldo = saldo + ganho if ganho > 0 else saldo - valor_apostado  
        # Atualizar banco de dados
        db.execute(
            "UPDATE users SET saldo = ?, ganhos = ganhos + ?, perdas = perdas + ? WHERE id = ?",
            saldo,
            ganho,
            valor_apostado if ganho == 0 else 0,
            user_id
        )
        return jsonify({
            "success": True,
            "novo_saldo": saldo,
            "mensagem": f"Você {'ganhou' if ganho > 0 else 'perdeu'} {ganho if ganho > 0 else valor_apostado} fichas! Resultado: {numero_sorteado} ({cor_resultado})",
            "message_class": "success" if ganho > 0 else "danger",
            "numero_sorteado": numero_sorteado
        })

    # GET: Renderizar a página normalmente
    return render_template('roleta.html', saldo=saldo, username=username)

@app.route('/niquel', methods=['GET', 'POST'])
@login_required
def niquel():
    symbols = ["🍒", "🍋", "⭐", "🔔", "🍀", "💎"]
    user_id = session.get('user_id')
    username = db.execute("SELECT username from users WHERE id = ?", user_id)[0]['username']
    saldo = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)[0]['saldo']
    grid = [[random.choice(symbols) for _ in range(3)] for _ in range(3)]

    if request.method == 'POST':
        try:
            aposta = float(request.form.get('aposta'))
        except (TypeError, ValueError):
            return render_template('niquel.html', saldo=saldo, grid=grid, 
                                 message="Valor de aposta inválido.", message_class="erro")

        if aposta < 1 or aposta > saldo:
            return render_template('niquel.html', saldo=saldo, grid=grid,
                                 message=f"Aposta deve ser entre 1 e {saldo:.1f}", message_class="erro")

        grid = [[random.choice(symbols) for _ in range(3)] for _ in range(3)]
        premiacao = calcular_premiacao(grid, aposta)

        if premiacao > 0:
            saldo += premiacao
            message = f"Você ganhou {premiacao:.1f} fichas"
            message_class = "ganhou"
            db.execute("UPDATE users SET saldo = ?, ganhos = ganhos + ? WHERE id = ?",
                     saldo, premiacao, user_id)
        else:
            saldo -= aposta
            message = f"Você Perdeu {aposta:.1f} fichas"
            message_class = "perdeu"
            db.execute("UPDATE users SET saldo = ?, perdas = perdas + ? WHERE id = ?",
                     saldo, aposta, user_id)

        return render_template('niquel.html', grid=grid, saldo=saldo,
                             message=message, message_class=message_class)

    return render_template("niquel.html", saldo=saldo, grid=grid, username=username)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id = session.get('user_id')
    username = db.execute("SELECT username from users WHERE id = ?", user_id)[0]['username']
    saldo = db.execute("SELECT saldo FROM users WHERE id = ?", user_id)[0]['saldo']
    if request.method == 'POST':
        try:
            fichas = int(request.form.get('fichas'))
            if fichas <= 0:
                raise ValueError
        except:
            flash("Valor inválido", "danger")
            return redirect(url_for('add'))
        
        db.execute("UPDATE users SET saldo = saldo + ? WHERE id = ?", fichas, user_id)
        flash(f"+{fichas} fichas adicionadas!", "success")
        return redirect(url_for('homepage'))
    
    return render_template('add.html', saldo=saldo, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Limpar os dados da sessão anterior
    #Checar se é POST
    if request.method == 'POST':
    #Pegar o username e senha
       username = request.form.get('username')
       password = request.form.get('password')
       #checar se usuario colocou username ou senha
       if not username or not password:
            flash("Credenciais inválidas!", "danger")
            return redirect(url_for('login'))
       #Obter usuario no db
       user = db.execute("SELECT * FROM users WHERE username = ?", username)
       #Verificar se usuario existe e se a senha esta correta
       if len(user) != 1 or not check_password_hash(user[0]['password'], password):
             flash("Senha ou usuário  inválidos", "danger")
             return redirect(url_for('login'))
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
    username = db.execute("SELECT username from users WHERE id = ?", user_id)[0]['username']
    saldo = db.execute("SELECT saldo from users WHERE id = ?", user_id)[0]['saldo']
    perdas = db.execute("SELECT perdas FROM users WHERE id = ?", user_id)[0]['perdas']
    ganhos = db.execute("SELECT ganhos FROM users WHERE id = ?", user_id)[0]['ganhos']
    if ganhos > perdas:
        total = ganhos - perdas
        message_class = "ganhou"
        mensagem = "Você ganhou"
    elif perdas > ganhos:
        total = perdas - ganhos
        message_class = "perdeu"
        mensagem = "Você perdeu"
    else:
        total = 0
        message_class = "empatou"   
        mensagem = "Você ganhou"     
    return render_template("historico.html", perdas=perdas, ganhos=ganhos, total=total, message_class=message_class, mensagem=mensagem, saldo=saldo, username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
   #Limpar a sessao anterior
    if request.method == "POST":
        #Obter os dados
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        #Checar se usuario prencheu todos os campos
        if not username or not password or not confirm:
             flash("Preencha todos os dados!", "danger")
             return redirect(url_for('register'))
        #checar se senha = confirmação
        if password != confirm:
             flash("Senhas não coincidem!", "danger")
             return redirect(url_for('register'))
        #Codificar a senha
        hashed_password = generate_password_hash(password)
        #Verificar se usuario ja existe
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if user:
             flash("Usuário já existe!", "danger")
             return redirect(url_for('register'))
        #Adicionar dados para db
        db.execute("INSERT INTO users (username, password, saldo, perdas, ganhos) VALUES(?, ?, ?, ?, ?)", username, hashed_password, 100, 0, 0)
        return redirect(url_for('login'))
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)