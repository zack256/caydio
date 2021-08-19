from flask import Flask, render_template, redirect, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import func as sql_func
import app.app_config as app_config
import app.encryption as encryption
import os

app = Flask(__name__)
app_config.configure_app(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique = True)
    registered = db.Column(db.DateTime(), default = db.func.now())

def create_user_from_form(username, password_plaintext, email):
    user = User()
    user.username = username
    user.password = encryption.hash_password(password_plaintext)
    user.email = email
    db.session.add(user)
    db.session.commit()

@app.route("/assets/<path:file_path>")
def get_asset_file(file_path):
    path = os.path.join(os.path.dirname(__file__), "assets")
    return send_from_directory(path, file_path, as_attachment = True)

@app.route("/")
def home_page():
    return "welcome to caydio!"

def ci_username_exists(username):
    # Case-Insensitive check.
    return User.query.filter(User.username.ilike(username)).first()
def ci_email_exists(email):
    return User.query.filter(User.email.ilike(email)).first()

@app.route("/register/", methods = ["GET", "POST"])
def register_page():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form["username"]
    password_plaintext = request.form["password"]
    email = request.form["email"]
    if ci_email_exists(email):
        return "Email already exists!"
    if ci_username_exists(username):
        return "Username already exists!"
    create_user_from_form(username, password_plaintext, email)
    return "successfully created."

@app.route("/users/<username>/")
def user_page(username):
    viewing_user = ci_username_exists(username)
    if not viewing_user:
        return "User does not exist!"
    return "User {} registered at {}.".format(viewing_user.username, viewing_user.registered)