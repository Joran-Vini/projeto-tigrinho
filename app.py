from cs50 import SQL
from flask import Flask, session, redirect, url_for, request

from help import login_required

app = Flask(__name__)
app.secret_key = 'Chave secreta!'
