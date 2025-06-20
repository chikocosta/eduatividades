
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def init_db():
    with sqlite3.connect("usuarios.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            plano TEXT DEFAULT 'gratis'
        )''')

@app.route('/')
def home():
    if 'email' in session:
        return send_from_directory('.', 'index.html')
    return redirect(url_for('login'))

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
            user = cursor.fetchone()
            if user:
                session['email'] = email
                session['plano'] = user[3]
                return redirect(url_for('home'))
            else:
                return "Login inválido"
    return send_from_directory('.', 'login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        with sqlite3.connect("usuarios.db") as conn:
            try:
                conn.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Usuário já existe"
    return send_from_directory('.', 'register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/gerar', methods=['POST'])
def gerar():
    if 'email' not in session:
        return jsonify({"atividade": "Erro: você precisa estar logado.", "gabarito": ""})

    exemplos = [
        ("Complete com os nomes dos animais da fazenda: O _____ faz muuu. A _____ põe ovos.", "Resposta: boi, galinha"),
        ("Ligue os animais às suas casinhas: [Boi] - [Curral], [Galinha] - [Galinheiro]", "Resposta: Boi-Curral, Galinha-Galinheiro"),
        ("Qual é o som de cada animal? Vaca: ____, Porco: ____, Cavalo: ____", "Resposta: Muu, Oinc, I-róó")
    ]

    atividade, gabarito = random.choice(exemplos)

    plano = session.get('plano', 'gratis')
    if plano == 'gratis':
        atividade += "\n\n--- MARCA-D'ÁGUA: GERADO NO EDUATIVIDADES.COM ---"

    return jsonify({"atividade": atividade, "gabarito": gabarito})

@app.route('/ativar_premium')
def ativar_premium():
    if 'email' in session:
        with sqlite3.connect("usuarios.db") as conn:
            conn.execute("UPDATE usuarios SET plano='premium' WHERE email=?", (session['email'],))
            conn.commit()
            session['plano'] = 'premium'
            return "Conta atualizada para Premium!"
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
