from flask import Flask, redirect, render_template, request, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import func as sql_func
import app.app_config as app_config
import app.encryption as encryption
import app.utils as utils
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
    a_tags = db.relationship("ArtistTag", backref = "user")

class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    added = db.Column(db.DateTime(), default = db.func.now())
    videos = db.relationship("VidConnection")
    a_tags = db.relationship("ATConn")
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete = 'CASCADE'))

    def get_readable_name(self):
        return self.name.replace("_", " ")

    def set_name(self, given_name):
        #self.name = given_name.replace(" ", "_")
        self.name = utils.artist_db_name(given_name)

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

class ArtistTag(db.Model):
    __tablename__ = "artist_tags"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(255))
    a_tags = db.relationship("ATConn")
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

class ATConn(db.Model):
    __tablename__ = "at_connections"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    artist_id = db.Column(db.Integer(), db.ForeignKey("artists.id"), primary_key = True, autoincrement = False)
    tag_id = db.Column(db.Integer(), db.ForeignKey("artist_tags.id"), primary_key = True, autoincrement = False)
    artist = db.relationship(Artist, backref = "artists_t")
    tag = db.relationship(ArtistTag, backref = "tags_t")

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
    user = get_logged_in_user()
    return render_template("index.html", user = user)

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

@app.route("/artists/")
def artists_page():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    artists = Artist.query.filter(Artist.user_id == user.id).order_by(Artist.name).all()
    return render_template("artists.html", artists = artists)

@app.route("/videos/")
def videos_page():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    videos = Video.query.filter(Video.user_id == user.id).order_by(Video.name).all()
    video_id_set = {video.id for video in videos}
    connections = VidConnection.query.filter(VidConnection.video_id.in_(video_id_set)).all()
    connection_set = {vid_con.artist_id for vid_con in connections}
    artists = Artist.query.filter(Artist.id.in_(connection_set)).all()
    artist_dict = {artist.id : artist for artist in artists}
    connection_dict = {}
    connections.sort(key = lambda x : artist_dict[x.artist_id].name)    # so the artist display list is sorted. maybe want to change.
    for connection in connections:
        if connection.video_id in connection_dict:
            connection_dict[connection.video_id].append(connection.artist_id)
        else:
            connection_dict[connection.video_id] = [connection.artist_id]
    return render_template("videos.html", videos = videos, artists = artist_dict, connections = connection_dict, list_artists = utils.comma_list_artists)

@app.route("/videos/<video_id>/")
def specific_video_page(video_id):
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    video = Video.query.get(int(video_id))
    if not video:
        return "Video not found!"
    if video.user_id != user.id:
        return "Can't access this video!"
    connections = video.artists
    connections_dict = {connections[i].artist_id : i for i in range(len(connections))}
    artists = Artist.query.filter(Artist.user_id == user.id).all()
    notes = []
    for i in range(len(artists)):
        if artists[i].id in connections_dict:
            notes.append((i, connections[connections_dict[artists[i].id]].note))
    notes.sort(key = lambda x : artists[x[0]].name)             # abc sorted, might change.
    return render_template("video.html", video = video, notes = notes, artists = artists)

@app.route("/artists/<artist_name>/")
def artist_page(artist_name):
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    artist = Artist.query.filter((Artist.name.ilike(artist_name) & (Artist.user_id == user.id))).first()
    if not artist:
        return "Artist not found!"
    conns = {conn.video_id : conn for conn in artist.videos}
    videos = Video.query.filter(Video.id.in_(conns)).order_by(Video.name).all()
    conns = [conns[video.id] for video in videos]
    return render_template("artist.html", artist = artist, videos = videos, conns = conns)

@app.route("/forms/add-artist/", methods = ["POST"])
def add_artist_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    na = request.form["name"]
    artist = Artist(); artist.set_name(na); artist.user_id = user.id
    if Artist.query.filter((Artist.user_id == user.id) & (Artist.name == na)).first():
        return "artist with same name already exists!"
    db.session.add(artist); db.session.commit()
    return redirect("/artists/{}/".format(artist.name))

@app.route("/forms/edit-artist/", methods = ["POST"])
def edit_artist_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    a = Artist.query.get(request.form["artistId"])
    if a.user_id != user.id:
        return "no access to edit this artist!"
    na = request.form.get("name", "")
    a.set_name(na)
    db.session.commit()
    return redirect("/artists/{}/".format(a.name))

def add_video(na, ur, user_id):
    video = Video(); video.name = na; video.youtube_url = ur; video.user_id = user_id
    db.session.add(video); db.session.commit()
    return video

def add_av_connection(a_id, v_id, note = ""):
    existing = VidConnection.query.filter((VidConnection.artist_id == a_id) & (VidConnection.video_id == v_id)).first()
    if existing:
        return None
    conn = VidConnection(); conn.artist_id = a_id; conn.video_id = v_id; conn.note = note
    db.session.add(conn); db.session.commit()
    return conn

@app.route("/forms/add-video-via-artist/", methods = ["POST"])
def add_vid_via_artist_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    ai = int(request.form["artistId"]); na = request.form.get("name", ""); ur = request.form["youtubeUrl"]
    video = add_video(na, ur, user.id)
    conn = add_av_connection(ai, video.id)
    if not conn:
        return "connection already exists!"
    artist = Artist.query.get(ai)
    return redirect("/artists/{}/".format(artist.name))

@app.route("/forms/connect-to-artist-via-video/", methods = ["POST"])
def add_artist_via_vid_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    vi = int(request.form["videoId"]); na = utils.artist_db_name(request.form.get("name")); note = request.form["note"]
    video = Video.query.get(vi)
    if video == None:
        return "video not found!"
    artist = Artist.query.filter((Artist.user_id == user.id) & (Artist.name == na)).first()     # artist must exist!
    conn = add_av_connection(artist.id, vi, note)
    if not conn:
        return "connection already exists!"
    return redirect("/videos/{}/".format(video.id))

@app.route("/forms/add-video/", methods = ["POST"])
def add_video_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    na = request.form.get("name", ""); ur = request.form["youtubeUrl"]
    add_video(na, ur, user.id)
    return redirect("/videos/")

@app.route("/forms/edit-video/", methods = ["POST"])
def edit_video_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    v = Video.query.get(request.form["videoId"])
    if v.user_id != user.id:
        return "no access to edit this video!"
    na = request.form.get("name", ""); ur = request.form["youtubeUrl"]
    v.name = na; v.youtube_url = ur
    db.session.commit()
    return redirect("/videos/{}/".format(v.id))

@app.route("/forms/delete-connection/", methods = ["POST"])
def delete_connection_route():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    conn_id = request.form["connID"]
    #conn = VidConnection.query.get({"vid_connections.id" : conn_id})
    conn = VidConnection.query.filter(VidConnection.id == conn_id).first()  # hmm...
    if not conn:
        return "conn don't exist"
    video = conn.video
    if video.user_id != user.id:
        return "no access to delete conn!"
    db.session.delete(conn)
    db.session.commit()
    return redirect("/videos/{}/".format(video.id))

@app.route("/add-conn/")
def add_conn():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    ar = request.args.get("ar"); vi = request.args.get("vi")
    conn = VidConnection(); conn.artist_id = int(ar); conn.video_id = int(vi)
    db.session.add(conn); db.session.commit()
    return redirect("/")

@app.route("/tags/")
def tags_pg():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    tags = sorted(user.a_tags, key = lambda x : x.name)
    return render_template("tags.html", tags = tags)

@app.route("/tags/<tag_name>/")
def tag_pg(tag_name):
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    tag = ArtistTag.query.filter((ArtistTag.user_id == user.id) & (ArtistTag.name == tag_name)).first()
    if not tag:
        return "tag doesn't exist!"
    return render_template("tag.html", tag = tag)

@app.route("/forms/add-tag/", methods = ["POST"])
def add_tag_form():
    user = get_logged_in_user()
    if not user:
        return "must log in first!"
    na = request.form["name"]; de = request.form["description"]
    name = utils.format_tag_name(na)
    if name == "":
        return "tag name invalid!"
    if ArtistTag.query.filter((ArtistTag.user_id == user.id) & (ArtistTag.name == name)).first():
        return "tag name already taken!"
    at = ArtistTag(name = name, description = de)
    at.user_id = user.id
    db.session.add(at); db.session.commit()
    return redirect("/tags/{}/".format(name))

@app.route("/refresh")
def rrr():
    # temporary. :)
    db.create_all()
    return "!"