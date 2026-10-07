import sqlite3
from pathlib import Path

from flashcards.database.schema import SCHEMA_STATEMENTS


def create_connection(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)

    connection.commit()
