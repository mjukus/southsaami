import os

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, url_for, send_from_directory
)
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("article", __name__)

  
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    body = CKEditorField("Body")
    image = FileField("Image", validators=[
        FileAllowed(["jpg", "png", "gif", "svg"], "Images only!")
    ])
    caption = CKEditorField("Caption")
    submit = SubmitField("Save")

def get_article(search, check_author=True):
    if type(search) is int:
        article = get_db().execute(
            "SELECT a.id, title, body, image, caption, created, author_id, username"
            " FROM article a JOIN user u on a.author_id = u.id"
            " WHERE a.id = ?",
            (search,)
        ).fetchone()
        if article is None:
            abort(404, f"Article id {search} doesn't exist.")
    elif type(search) is str:
        processed_search = search.replace("%20", " ")
        article = get_db().execute(
            "SELECT a.id, title, body, image, caption, created, author_id, username"
            " FROM article a JOIN user u on a.author_id = u.id"
            " WHERE a.title = ?",
            (processed_search,)
        ).fetchall()
        if len(article) == 0:
            abort(404, f"No article by the title {search} exists. Titles are case sensitive.")
        elif len(article) > 1:
            abort(400, f"Multiple articles with title {search}. Please use an ID instead.")
        article = article[0]
    else:
        raise TypeError("get_article() takes a search of type int or str only.")

    if check_author and article["author_id"] != g.user["id"]:
        abort(403)

    return article

@bp.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(current_app.instance_path, filename)

@bp.route("/index")
@login_required
def index():
    return render_template("article/index.html")

@bp.route("/<int:id>")
def view_by_id(id=1):
    article = get_article(id, check_author=False)
    return render_template("article/page.html", article=article)

@bp.route("/<title>")
def view_by_title(title):
    article = get_article(title, check_author=False)
    return render_template("article/page.html", article=article)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(
                current_app.instance_path, filename
            ))
        caption = form.caption.data

        db = get_db()
        db.execute(
            "INSERT INTO article (title, body, image, caption, author_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (title, body, filename, caption, g.user["id"])
        )
        db.commit()
        return redirect(url_for("article.index"))
    
    else:
        if form.errors:
            for error in form.errors:
                current_app.logger.error("An error occurred during validation: %s", error)
                flash(error)
        else:
            current_app.logger.info("Request method is not post.")

    return render_template("article/create.html", form=form)

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    article = get_article(id)
    form = PostForm()
    form.title.data = article["title"]
    form.body.data = article["body"]
    form.caption.data = article["caption"]

    if form.validate_on_submit():
        db = get_db()
        title = form.title.data
        body = form.body.data
        image = form.image.data
        caption = form.caption.data
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(
                current_app.instance_path, filename
            ))
            db.execute(
                "UPDATE article SET title = ?, body = ?, image = ?, caption = ?"
                " WHERE id = ?",
                (title, body, filename, caption, id)
            )
            db.commit()
        else:
            db.execute(
                "UPDATE article SET title = ?, body = ?, caption = ?"
                " WHERE id = ?",
                (title, body, caption, id)
            )
            db.commit()

        return redirect(url_for("article.index"))
    
    else:
        if form.errors:
            for error in form.errors:
                current_app.logger.error("An error occurred during validation: %s", error)
                flash(error)
        else:
            current_app.logger.error("Request method is not post.")
    
    return render_template("article/update.html", article=article, form=form)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    article = get_article(id)
    if article["image"]:
        try:
            os.remove(os.path.join(
                current_app.instance_path, article["image"]
            ))
        except IOError as e:
            current_app.logger.exception("No such file %", e)
    db = get_db()
    db.execute("DELETE FROM article WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("article.index"))