from flask import redirect, url_for, session
from functools import wraps
import random
def login_required(f):
    "Decorate routes to require login"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

def calcular_premiacao(grid, aposta):
    premiacao = 0
    multiplicadores = {
        "linha": 2.0,
        "coluna": 1.5,
        "diagonal": 5.0
    }

    # Verificar linhas
    for row in grid:
        if len(set(row)) == 1:
            premiacao += aposta * multiplicadores["linha"]

    # Verificar colunas
    for col in range(3):
        column = [grid[row][col] for row in range(3)]
        if len(set(column)) == 1:
            premiacao += aposta * multiplicadores["coluna"]

    # Verificar diagonais
    diagonal1 = [grid[i][i] for i in range(3)]
    diagonal2 = [grid[i][2-i] for i in range(3)]
    if len(set(diagonal1)) == 1:
        premiacao += aposta * multiplicadores["diagonal"]
    if len(set(diagonal2)) == 1:
        premiacao += aposta * multiplicadores["diagonal"]

    return round(premiacao, 2)
    