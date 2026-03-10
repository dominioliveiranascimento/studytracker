from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "737373"

def criar_tabela():
    conexao = sqlite3.connect("meu_banco.db")
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
    conexao = sqlite3.connect("meu_banco.db")
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

    conexao = sqlite3.connect("meu_banco.db")
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
    
    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    user_id = session["user_id"]
    
    cursor.execute(
        "SELECT * FROM estudos WHERE user_id = ? ",
        (user_id,)
    )

    dados = cursor.fetchall()

    conexao.close()

    return render_template("history.html", dados=dados)


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
            WHERE id ? = AND user_id = ?
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

        conexao = sqlite3.connect("meu_banco.db")
        cursor = conexao.cursor()

        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)",
         (username, password))

        conexao.commit()
        conexao.close()

        return redirect("/login")


    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")

        conexao = sqlite3.connect("meu_banco.db")
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE username = ? AND PASSWORD = ?", (username, password)
        )

        usuario = cursor.fetchone()

        conexao.close()

        if usuario:
            session["user_id"] = usuario[0]
            return redirect("/")
        
        else:
            return "Usuário ou senha inválidos"
        
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)