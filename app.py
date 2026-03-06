from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def criar_tabela():
    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia TEXT,
            tempo INTEGER,
            data TEXT
        )
    """)
    conexao.commit()
    conexao.close()

criar_tabela()

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/save", methods=["POST"])
def salvar_dados():
    materia = request.form.get('materia')
    tempo = request.form.get("tempo")
    data = request.form.get("data")

    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO estudos (materia, tempo, data) VALUES (?, ?, ?)",
        (materia, tempo, data)
    )
    
    conexao.commit()
    conexao.close()

    return redirect("/history")

@app.route("/history")
def historico():
    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM estudos")

    dados = cursor.fetchall()

    conexao.close()

    return render_template("history.html", dados=dados)

if __name__ == "__main__":
    app.run(debug=True)