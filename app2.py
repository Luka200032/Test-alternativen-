import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates2", static_folder="static2")
app.secret_key = "tajni_kljuc_2"

UPLOAD_FOLDER = "static2/slike"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = TinyDB("db/socialna.json")
users = db.table("users")
objave = db.table("objave")
lajki = db.table("lajki")
User = Query()
Objava = Query()
Lajk = Query()


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    vse = objave.all()
    vse.reverse()  # najnovejše najprej
    return render_template("index.html", objave=vse, user=session["user"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ime = request.form["ime"]
        geslo = request.form["geslo"]
        if users.search(User.ime == ime):
            return render_template("register.html", napaka="Uporabnik že obstaja")
        users.insert({"ime": ime, "geslo": generate_password_hash(geslo)})
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ime = request.form["ime"]
        geslo = request.form["geslo"]
        u = users.search(User.ime == ime)
        if u and check_password_hash(u[0]["geslo"], geslo):
            session["user"] = ime
            return redirect(url_for("index"))
        return render_template("login.html", napaka="Napačno ime ali geslo")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/objavi", methods=["GET", "POST"])
def objavi():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        besedilo = request.form["besedilo"]
        slika_ime = ""
        if "slika" in request.files:
            slika = request.files["slika"]
            if slika.filename != "":
                ime = secure_filename(slika.filename)
                slika.save(os.path.join(UPLOAD_FOLDER, ime))
                slika_ime = ime
        objave.insert({"avtor": session["user"], "besedilo": besedilo, "slika": slika_ime, "lajki": 0})
        return redirect(url_for("index"))
    return render_template("objavi.html")


@app.route("/brisi/<int:oid>")
def brisi(oid):
    if "user" not in session:
        return redirect(url_for("login"))
    o = objave.get(doc_id=oid)
    if o and o["avtor"] == session["user"]:
        objave.remove(doc_ids=[oid])
    return redirect(url_for("index"))


# AJAX - lajkanje objave
@app.route("/lajk/<int:oid>", methods=["POST"])
def lajk(oid):
    if "user" not in session:
        return jsonify({"napaka": "Nisi prijavljen"}), 401
    user = session["user"]
    # Preveri ali je že lajkal
    ze_lajkal = lajki.search((Lajk.user == user) & (Lajk.objava == oid))
    o = objave.get(doc_id=oid)
    if not o:
        return jsonify({"napaka": "Ni objave"}), 404
    if ze_lajkal:
        # Odstrani lajk
        lajki.remove((Lajk.user == user) & (Lajk.objava == oid))
        novo = o["lajki"] - 1
        objave.update({"lajki": novo}, doc_ids=[oid])
        return jsonify({"lajki": novo, "lajkal": False})
    else:
        # Dodaj lajk
        lajki.insert({"user": user, "objava": oid})
        novo = o["lajki"] + 1
        objave.update({"lajki": novo}, doc_ids=[oid])
        return jsonify({"lajki": novo, "lajkal": True})


# Zunanji API - vremenska napoved (za oceno 3)
@app.route("/vreme")
def vreme():
    import requests
    try:
        r = requests.get("https://wttr.in/Ljubljana?format=j1", timeout=5)
        podatki = r.json()
        temp = podatki["current_condition"][0]["temp_C"]
        opis = podatki["current_condition"][0]["weatherDesc"][0]["value"]
    except Exception:
        temp = "?"
        opis = "Napaka pri pridobivanju"
    return jsonify({"temp": temp, "opis": opis})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
