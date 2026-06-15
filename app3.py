from flask import Flask, render_template, request, jsonify, session
from tinydb import TinyDB

app = Flask(__name__, template_folder="templates3")
app.secret_key = "skrivni_kljuc"

db = TinyDB("rezultati.json")

VPRASANJA = [
    {
        "vprasanje": "Kaj je glavno mesto Slovenije?",
        "moznosti": ["Maribor", "Ljubljana", "Celje", "Kranj"],
        "pravilno": 1
    },
    {
        "vprasanje": "Koliko je 7 × 8?",
        "moznosti": ["54", "56", "58", "62"],
        "pravilno": 1
    },
    {
        "vprasanje": "Kaj je H2O?",
        "moznosti": ["Sol", "Voda", "Kisik", "Vodik"],
        "pravilno": 1
    }
]


@app.route("/")
def index():
    session["tocke"] = 0
    return render_template("index.html", vprasanja=VPRASANJA)


@app.route("/preveri", methods=["POST"])
def preveri():
    data = request.get_json()

    vprasanje_id = data["id"]
    izbira = data["izbira"]

    pravilno = izbira == VPRASANJA[vprasanje_id]["pravilno"]

    if pravilno:
        session["tocke"] = session.get("tocke", 0) + 1

    return jsonify({
        "pravilno": pravilno,
        "tocke": session["tocke"]
    })


@app.route("/shrani", methods=["POST"])
def shrani():
    ime = request.form["ime"]

    db.insert({
        "ime": ime,
        "tocke": session.get("tocke", 0)
    })

    session.clear()

    return "Rezultat uspešno shranjen!"


if __name__ == "__main__":
    app.run(debug=True)