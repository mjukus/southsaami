import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get("/index")
    assert response.headers["Location"] == "/auth/login"

    auth.login()
    response = client.get("/index")
    assert b"Log Out" in response.data
    assert b"test title" in response.data
    assert b"test\nbody" in response.data  # Fails here?
    assert b"test caption" in response.data
    assert b"href='/images/test_image.jpg'" in response.data
    assert b"href='/1/update'" in response.data


@pytest.mark.parametrize("path", (
    "/create",
    "/1/update",
    "/1/delete",
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute("UPDATE article SET author_id = 2 where id = 1")
        db.commit()

    auth.login()
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    assert b"href='/1/update'" not in client.get("/index").data


@pytest.mark.parametrize("path", (
    "/2/update",
    "/2/delete",
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM article").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        article = db.execute("SELECT * FROM article WHERE id = 1").fetchone()
        assert article["title"] == "updated"


@pytest.mark.parametrize("path", (
    "/create",
    "/1/update",
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data  # Errors don't appear atm. Idky.


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/index"

    with app.app_context():
        db = get_db()
        article = db.execute("SELECT * FROM article WHERE id = 1").fetchone()
        assert article is None