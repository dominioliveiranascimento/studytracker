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


@app.route("/delete/<int:id>", methods=["POST"])
def deletar(id):
    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM estudos WHERE id = ?", (id,))

    conexao.commit()
    conexao.close()

    return redirect("/history")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def editar(id):
    
    conexao = sqlite3.connect("meu_banco.db")
    cursor = conexao.cursor()

    if request.method == "POST":
        materia = request.form.get("materia")
        tempo = request.form.get("tempo")
        data = request.form.get("data")

        cursor.execute("""
            UPDATE estudos 
            SET materia = ?, tempo = ?, data = ?
            WHERE id = ?
""", (materia, tempo, data, id))

        conexao.commit()
        conexao.close()

        return redirect("/history")
    
    cursor.execute("SELECT * FROM estudos WHERE id = ?", (id,))
    estudo = cursor.fetchone()

    conexao.close

    return render_template("edit.html", estudo=estudo)

if __name__ == "__main__":
    app.run(debug=True)