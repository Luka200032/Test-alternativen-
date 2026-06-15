import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tinydb import TinyDB
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates2", static_folder="static2")
app.secret_key = "123"

UPLOAD_FOLDER = "static2/slike"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = TinyDB("db.json")
objave = db.table("objave")


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    vse = objave.all()
    vse.reverse()

    return render_template("index.html", objave=vse, user=session["user"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["ime"]
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/objavi", methods=["POST"])
def objavi():
    if "user" not in session:
        return redirect(url_for("login"))

    besedilo = request.form["besedilo"]
    slika_ime = ""

    if "slika" in request.files:
        slika = request.files["slika"]
        if slika.filename != "":
            ime = secure_filename(slika.filename)
            slika.save(os.path.join(UPLOAD_FOLDER, ime))
            slika_ime = ime

    objave.insert({
        "user": session["user"],
        "besedilo": besedilo,
        "slika": slika_ime,
        "lajki": 0
    })

    return redirect(url_for("index"))


@app.route("/like/<int:oid>", methods=["POST"])
def like(oid):
    o = objave.get(doc_id=oid)
    if not o:
        return jsonify({"error": "Ni objave"})

    novo = o["lajki"] + 1
    objave.update({"lajki": novo}, doc_ids=[oid])

    return jsonify({"lajki": novo})


if __name__ == "__main__":
    app.run(debug=True)