import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()
    
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialised" in result.output
    assert Recorder.called
    

# @pytest.mark.parametrize(('username', 'password', 'message'), (
#         ("a", "a", b"a registered."),
#         ("", "", b"Username is required."),
#         ("a", "", b"Password is required."),
#         ("test", "test", b"already registered"),
# ))
# def test_register_command(runner, monkeypatch, app, username, password, message):
#     class Recorder(object):
#         called = False

#     def fake_register():
#         Recorder.called = True

#     monkeypatch.setattr("flaskr.db.register", fake_register)
#     result = runner.invoke(args=["register", username, password])
#     assert message in result.output
#     assert Recorder.called

#     if message == "a registered":
#         with app.app_context():
#             assert get_db().execute(
#                 "SELECT * FROM user WHERE username = 'a'",
#             ).fetchone() is not None
