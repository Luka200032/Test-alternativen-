from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates1", static_folder="static1")
app.secret_key = "tajni_kljuc_1"

db = TinyDB("db/zapiski.json")
users = db.table("users")
zapiski = db.table("zapiski")
User = Query()
Zapisek = Query()


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    moji = zapiski.search(Zapisek.avtor == session["user"])
    return render_template("index.html", zapiski=moji)


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


@app.route("/nov", methods=["GET", "POST"])
def nov():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        naslov = request.form["naslov"]
        vsebina = request.form["vsebina"]
        zapiski.insert({"naslov": naslov, "vsebina": vsebina, "avtor": session["user"]})
        return redirect(url_for("index"))
    return render_template("nov.html")


@app.route("/uredi/<int:zid>", methods=["GET", "POST"])
def uredi(zid):
    if "user" not in session:
        return redirect(url_for("login"))
    z = zapiski.get(doc_id=zid)
    if not z or z["avtor"] != session["user"]:
        return redirect(url_for("index"))
    if request.method == "POST":
        zapiski.update({"naslov": request.form["naslov"], "vsebina": request.form["vsebina"]}, doc_ids=[zid])
        return redirect(url_for("index"))
    return render_template("uredi.html", z=z, zid=zid)


@app.route("/brisi/<int:zid>")
def brisi(zid):
    if "user" not in session:
        return redirect(url_for("login"))
    z = zapiski.get(doc_id=zid)
    if z and z["avtor"] == session["user"]:
        zapiski.remove(doc_ids=[zid])
    return redirect(url_for("index"))


# AJAX - iskanje zapiskov
@app.route("/iskanje")
def iskanje():
    q = request.args.get("q", "").lower()
    moji = zapiski.search(Zapisek.avtor == session.get("user", ""))
    rezultati = [z for z in moji if q in z["naslov"].lower() or q in z["vsebina"].lower()]
    return jsonify(rezultati)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
