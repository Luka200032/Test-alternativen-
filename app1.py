from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from tinydb import TinyDB

app = Flask(__name__, template_folder="templates1")
app.secret_key = "123"

db = TinyDB("db.json")
zapiski = db.table("zapiski")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["ime"]
        return redirect(url_for("index.html"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("index.html", zapiski=zapiski.all())


@app.route("/add", methods=["POST"])
def add():
    zapiski.insert({
        "naslov": request.form["naslov"],
        "vsebina": request.form["vsebina"]
    })
    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete(id):
    zapiski.remove(doc_ids=[id])
    return redirect(url_for("index"))


@app.route("/search")
def search():
    q = request.args.get("q", "").lower()

    res = [
        z for z in zapiski.all()
        if q in z["naslov"].lower() or q in z["vsebina"].lower()
    ]

    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=True)