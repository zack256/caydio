from flask import Flask, redirect, render_template, request, send_from_directory, session
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
    artists = db.relationship("Artist", backref = "user")
    videos = db.relationship("Video", backref = "user")

class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    added = db.Column(db.DateTime(), default = db.func.now())
    videos = db.relationship("VidConnection")
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete = 'CASCADE'))

class Video(db.Model):
    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    youtube_url = db.Column(db.String(50))
    added = db.Column(db.DateTime(), default = db.func.now())
    artists = db.relationship("VidConnection")
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete = 'CASCADE'))

class VidConnection(db.Model):
    __tablename__ = "vid_connections"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    artist_id = db.Column(db.Integer(), db.ForeignKey("artists.id"), primary_key = True, autoincrement = False)
    video_id = db.Column(db.Integer(), db.ForeignKey("videos.id"), primary_key = True, autoincrement = False)
    artist = db.relationship(Artist, backref = "artists_c")
    video = db.relationship(Video, backref = "videos_c")
    note = db.Column(db.String(255))

def create_user_from_form(username, password_plaintext, email):
    user = User()
    user.username = username
    user.password = encryption.hash_password(password_plaintext)
    user.email = email
    db.session.add(user)
    db.session.commit()
    return user

@app.route("/assets/<path:file_path>")
def get_asset_file(file_path):
    path = os.path.join(os.path.dirname(__file__), "assets")
    return send_from_directory(path, file_path, as_attachment = True)

@app.route("/")
def home_page():
    return render_template("index.html")

def ci_username_exists(username):
    # Case-Insensitive check.
    return User.query.filter(User.username.ilike(username)).first()
def ci_email_exists(email):
    return User.query.filter(User.email.ilike(email)).first()

def add_user_id_to_session(user_id):
    session["user_id"] = user_id

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
    user = create_user_from_form(username, password_plaintext, email)
    add_user_id_to_session(user.id)
    return redirect("/")

@app.route("/users/<username>/")
def user_page(username):
    viewing_user = ci_username_exists(username)
    if not viewing_user:
        return "User does not exist!"
    return "User {} registered at {}.".format(viewing_user.username, viewing_user.registered)

@app.route("/logout/")
def logout():
    session.pop("user_id", None)
    return redirect("/")

def user_is_logged_in():
    return session.get("user_id", -1) != -1

def get_logged_in_user():
    user_id = int(session.get("user_id", -1))
    if user_id == -1:
        return None
    return User.query.get(user_id)

@app.route("/login/", methods = ["GET", "POST"])
def login_page():
    if request.method == "GET":
        if get_logged_in_user():
            return redirect("/")
        return render_template("login.html")
    else:
        username = request.form["username"]
        user = User.query.filter(User.username == username).first()
        if not user:
            return "username not found."
        password_plaintext = request.form["password"]
        hashed_password = user.password
        if not encryption.verify_password(password_plaintext, hashed_password):
            return "password is incorrect!"
        add_user_id_to_session(user.id)
        return redirect("/")

@app.route("/artists/<artist_name>/")
def artist_page(artist_name):
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    artist = Artist.query.filter((Artist.name.ilike(artist_name) & (Artist.user_id == user.id))).first()
    if not artist:
        return "Artist not found!"
    conns = {conn.video_id for conn in artist.videos}
    videos = Video.query.filter(Video.id.in_(conns)).order_by(Video.name).all()
    return render_template("artist.html", artist = artist, videos = videos)

@app.route("/add-artist/")
def add_artist():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    na = request.args.get("na")
    artist = Artist(); artist.name = na; artist.user_id = user.id
    db.session.add(artist); db.session.commit()
    return redirect("/")
@app.route("/add-video/")
def add_video():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    na = request.args.get("na"); ur = request.args.get("ur")
    video = Video(); video.name = na; video.youtube_url = ur; video.user_id = user.id
    db.session.add(video); db.session.commit()
    return redirect("/")
@app.route("/add-conn/")
def add_conn():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    ar = request.args.get("ar"); vi = request.args.get("vi")
    conn = VidConnection(); conn.artist_id = int(ar); conn.video_id = int(vi)
    db.session.add(conn); db.session.commit()
    return redirect("/")
@app.route("/refresh")
def rrr():
    db.create_all()
    return "!"
