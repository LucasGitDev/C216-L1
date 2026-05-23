import os

from flask import Flask, flash, redirect, render_template, request, url_for
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

API_URL = os.getenv("API_URL", "http://backend:8000/api/v1/professores")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        data = {
            "nome": request.form["nome"],
            "email": request.form["email"],
            "sala_de_atendimento": request.form["sala_de_atendimento"],
        }
        response = requests.post(API_URL, json=data)
        if response.status_code == 201:
            flash("Professor cadastrado com sucesso!", "success")
            return redirect(url_for("professores"))
        detail = _detail(response, "Erro ao cadastrar professor.")
        flash(detail, "danger")
    return render_template("cadastro.html")


@app.route("/professores")
def professores():
    response = requests.get(API_URL)
    items = response.json().get("items", []) if response.ok else []
    return render_template("professores.html", professores=items)


@app.route("/editar/<int:professor_id>", methods=["GET", "POST"])
def editar(professor_id):
    if request.method == "POST":
        data = {
            "nome": request.form["nome"],
            "email": request.form["email"],
            "sala_de_atendimento": request.form["sala_de_atendimento"],
        }
        response = requests.patch(f"{API_URL}/{professor_id}", json=data)
        if response.ok:
            flash("Professor atualizado com sucesso!", "success")
        else:
            flash(_detail(response, "Erro ao atualizar professor."), "danger")
        return redirect(url_for("professores"))
    prof = requests.get(f"{API_URL}/{professor_id}").json()
    return render_template("editar.html", professor=prof)


@app.route("/excluir/<int:professor_id>")
def excluir(professor_id):
    response = requests.delete(f"{API_URL}/{professor_id}")
    if response.ok:
        flash("Professor removido com sucesso!", "success")
    else:
        flash(_detail(response, "Erro ao remover professor."), "danger")
    return redirect(url_for("professores"))


@app.route("/reset")
def reset():
    response = requests.delete(API_URL)
    if response.ok:
        flash("Banco de dados resetado com sucesso!", "info")
    else:
        flash(_detail(response, "Erro ao resetar banco."), "danger")
    return redirect(url_for("home"))


def _detail(response, fallback):
    try:
        return response.json().get("detail", fallback)
    except ValueError:
        return fallback


if __name__ == "__main__":
    app.run(debug=True, port=3000, host="0.0.0.0")
