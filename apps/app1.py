from flask import Flask, render_template, request, redirect, jsonify, session
from tinydb import TinyDB

# templates vljuc html datoteke v aplikacijo
# static vkljuc json in css datoteke
app = Flask(__name__,
    template_folder="templates",
    static_folder="static1")

# kljuc za session
app.secret_key = "123"

# povezava teh baz k shranjo zapiske
db = TinyDB("notes1.json")


# zacetna stran
@app.route("/")
def index():
    #session shranimo dijaka
    session["user"] = "dijak"

    # prebere vse zapiske iz baze
    notes = db.all()

    # posle zapiske v html
    return render_template(
        "template1.html",
        notes=notes
    )


# dodajanje zapiska
@app.route("/add", methods=["POST"])
def add():

    # vzame podatke iz forme pa jih shran v bazo
    db.insert({
        "title": request.form["title"],
        "content": request.form["content"]
    })

    # vrne nazaj na glavno stran
    return redirect("/")


# zbrise zapiske
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    # zbirse po idju
    db.remove(doc_ids=[id])

    # da odgovor za ajax
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)