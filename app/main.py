from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import app.app_config as app_config

app = Flask(__name__)
app_config.configure_app(app)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(255), unique=True)

@app.route("/")
def home_page():
    return "welcome to caydio!"