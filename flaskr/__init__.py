import os

from flask import Flask
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect

from . import auth, article, db

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        UPLOAD_FOLDER=os.path.join("/static/images/")
    )
    ckeditor = CKEditor()
    csrf = CSRFProtect()

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    ckeditor.init_app(app)
    csrf.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(article.bp)
    app.add_url_rule("/", view_func=article.view_by_id)

    @app.context_processor  # Bit of a fudge to put it here
    def get_articles():     # Unfortunately no nav at / otherwise
        data = db.get_db()
        articles = data.execute(
            "SELECT a.id, title, body, image, caption, created, author_id, username"
            " FROM article a JOIN user u ON a.author_id = u.id"
            " ORDER BY created ASC"
        ).fetchall()
        return {"articles": articles}

    return app

app = create_app()
