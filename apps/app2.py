from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "123"

db_users = TinyDB("db2/users.json")
db_posts = TinyDB("db2/posts.json")

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    posts = db_posts.all()
    return render_template("template2.html", posts=posts, user=session["user"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        User = Query()
        user = db_users.search((User.username == u) & (User.password == p))

        if user:
            session["user"] = u
            return redirect("/")
        return "napaka login"

    return render_template("template1.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db_users.insert({
            "username": request.form["username"],
            "password": request.form["password"]
        })
        return redirect("/login")

    # če nimaš register posebej, lahko uporabiš template1 ali ga dodamo kasneje
    return render_template("template1.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        db_posts.insert({
            "text": request.form["text"],
            "author": session["user"]
        })
        return redirect("/")

    return render_template("template3.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)