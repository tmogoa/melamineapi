from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import click
import sqlite3

db = SQLAlchemy()

def get_db():
    db_ = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    db_.row_factory = sqlite3.Row
    return db_

def define_db():
    db_ = get_db();
    with current_app.open_resource('db/schema.sql') as f:
        db_.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    define_db()
    click.echo('Initialized the database.')

def init_db(app):
    print(app)
    app.cli.add_command(init_db_command)