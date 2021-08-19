import os

def fix_pg_db_url(s):
    if s.startswith('postgres://"'):
        s = s.replace("postgres://", "postgresql://", 1)
    return s

def configure_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = fix_pg_db_url(os.environ["DATABASE_URL"])
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
    app.config['CSRF_ENABLED'] = True