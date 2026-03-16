from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.secret_key = "737373"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "meu_banco.db")

conexao = sqlite3.connect(DB_PATH)

def criar_tabela():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            materia TEXT,
            tempo INTEGER,
            data TEXT
        )
    """)
    conexao.commit()
    conexao.close()

def criar_tabela_usuarios():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, 
            password TEXT)
""")
    conexao.commit()
    conexao.close()

criar_tabela()
criar_tabela_usuarios()


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    
    return render_template("index.html")


@app.route("/save", methods=["POST"])
def salvar_dados():

    if "user_id" not in session:
        return redirect("/login")

    materia = request.form.get('materia')
    tempo = request.form.get("tempo")
    data = request.form.get("data")

    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()


    user_id = session["user_id"]

    cursor.execute(
    "INSERT INTO estudos (user_id, materia, tempo, data) VALUES (?, ?, ?, ?)",
    (user_id, materia, tempo, data)
)
    
    conexao.commit()
    conexao.close()

    return redirect("/history")

@app.route("/history")
def historico():

    if "user_id" not in session:
        return redirect("/login")
    
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    user_id = session["user_id"]
    
    cursor.execute(
        "SELECT * FROM estudos WHERE user_id = ? ",
        (user_id,)
    )

    dados = cursor.fetchall()

    conexao.close()

    return render_template("history.html", dados=dados)

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT SUM(tempo) FROM estudos WHERE user_id = ?",
        (user_id,)
    )

    tempo_total = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM estudos WHERE user_id = ?",
        (user_id,)
    )

    total_sessoes = cursor.fetchone()[0]
    cursor.execute("""
        SELECT materia, SUM(tempo) as total
        FROM estudos
        WHERE user_id = ? 
        GROUP BY materia 
        ORDER BY total DESC 
        LIMIT 3
""", (user_id,))
    
    materia_top = cursor.fetchall()

    conexao.close()

    return render_template(
        "dashboard.html",
        tempo_total = tempo_total,
        total_sessoes = total_sessoes,
        materia_top = materia_top
)

@app.route("/save-timer", methods=["POST"])
def save_timer():
    data = request.get_json()

    tempo = data["tempo"]

    materia = "Timer"

    user_id = session["user_id"]

    hoje = datetime.date.today()

    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()


    cursor.execute("""
        INSERT INTO estudos (user_id, materia, tempo, data)
        VALUES (?, ?, ?, ?)
""", (user_id, materia, tempo, hoje))
    

    conexao.commit()
    conexao.close()

    return jsonify({"status": "ok"})

@app.route("/delete/<int:id>", methods=["POST"])
def deletar(id):

    if "user_id" not in session:
        return redirect("/login")

    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM estudos WHERE id = ? AND user_id = ?", 
        (id, session["user_id"])
    )

    conexao.commit()
    conexao.close()

    return redirect("/history")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def editar(id):

    if "user_id" not in session:
        return redirect("/login")
    
    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    if request.method == "POST":
        materia = request.form.get("materia")
        tempo = request.form.get("tempo")
        data = request.form.get("data")

        cursor.execute("""
            UPDATE estudos 
            SET materia = ?, tempo = ?, data = ?
            WHERE id = ? AND user_id = ?
""", (materia, tempo, data, id, session["user_id"]))

        conexao.commit()
        conexao.close()

        return redirect("/history")
    
    cursor.execute("SELECT * FROM estudos WHERE id = ? AND  user_id = ?", (id, session["user_id"]))
    estudo = cursor.fetchone()

    conexao.close()

    return render_template("edit.html", estudo=estudo)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        senha_hash = generate_password_hash(password)

        try:
            conexao = sqlite3.connect("meu_banco.db")
            cursor = conexao.cursor()

            cursor.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                (username, senha_hash)
            )

            conexao.commit()
            conexao.close()

            return redirect("/login")
        
        except sqlite3.IntegrityError:
            conexao.close()
            return render_template("register.html", erro="Esse usuário já existe.")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")

        conexao = sqlite3.connect("meu_banco.db")
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        )

        usuario = cursor.fetchone()

        conexao.close()

        if usuario and check_password_hash(usuario[2], password):
            session["user_id"] = usuario[0]
            return redirect("/")
        
        else:
            return "Usuário ou senha inválidos"
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


#PORT = int(os.environ.get("PORT", 5000))
    
#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=PORT)
    
