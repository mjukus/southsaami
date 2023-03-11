import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    '''
    If g has an attribute db, i.e. a connection was made to the db, 
    then the attribute is removed and returned and the db is closed.
    '''
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-db")
def init_db_command():
    '''Clear the existing data and create new tables.'''
    init_db()
    click.echo("Initialised the database.")

def register(username, password):
    db = get_db()
    error = None
    if not username:
        error = "Username is required."
    if not password:
        error = "Password is required."
    if error is None:
        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
            error = f"User {username} is already registered."
        else:
            return f"User {username} registered."
        
    return error

@click.command("register")
@click.option("--username", prompt="Username",
              help="The name the user will log in with.")
@click.option("--password", prompt="Password",
              help="The password the user will verify their identity with.")
def register_command(username, password):
    '''Register a new user to the database.'''
    click.echo(register(username, password))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(register_command)
