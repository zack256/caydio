from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
import app.app_config as app_config
import app.encryption as encryption

app = Flask(__name__)
app_config.configure_app(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique = True)

def create_user_from_form(username, password_plaintext, email):
    user = User()
    user.username = username
    user.password = encryption.hash_password(password_plaintext)
    user.email = email
    db.session.add(user)
    db.session.commit()

@app.route("/")
def home_page():
    return "welcome to caydio!"