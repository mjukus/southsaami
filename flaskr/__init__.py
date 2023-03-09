import os

from flask import Flask, render_template

from . import db, auth, article


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite")
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    
    os.makedirs(app.instance_path, exist_ok=True)

    # @app.route("/")
    # def index():
    #     return render_template("index.html")
    

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(article.bp)
    app.add_url_rule("/", view_func=article.view_by_id)

    return app
