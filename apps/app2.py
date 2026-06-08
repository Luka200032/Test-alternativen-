from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB

app = Flask(__name__,template_folder="templates2",static_folder="static2")

app.secret_key = "secret123"

users_db = TinyDB("db/users.json")
posts_db = TinyDB("db/posts.json")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]


if __name__ == "__main__":
    app.run(debug=True, port=5001)