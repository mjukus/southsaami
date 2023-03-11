from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("article", __name__)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form.get("ckeditor")
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO article (title, body, author_id)"
                " VALUES (?, ?, ?)",
                (title, body, g.user["id"])
            )
            db.commit()
            return redirect(url_for("article.index"))
    
    return render_template("article/create.html")


def get_article(search, check_author=True):
    if type(search) is int:
        article = get_db().execute(
            "SELECT a.id, title, body, created, author_id, username"
            " FROM article a JOIN user u on a.author_id = u.id"
            " WHERE a.id = ?",
            (search,)
        ).fetchone()
        if article is None:
            abort(404, f"Article id {search} doesn't exist.")
    elif type(search) is str:
        processed_search = search.replace("%20", " ")
        article = get_db().execute(
            "SELECT a.id, title, body, created, author_id, username"
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

@bp.route("/index")
@login_required
def index():
    return render_template("article/index.html")

@bp.route("/<int:id>")
def view_by_id(id=1):
    article = get_article(id)
    return render_template("article/page.html", article=article)

@bp.route("/<title>")
def view_by_title(title):
    article = get_article(title)
    return render_template("article/page.html", article=article)

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    article = get_article(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form.get("ckeditor")
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE article SET title = ?, body = ?"
                " WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("article.index"))
    
    return render_template("article/update.html", article=article)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_article(id)
    db = get_db()
    db.execute("DELETE FROM article WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("article.index"))
