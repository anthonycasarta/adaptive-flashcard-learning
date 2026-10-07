import sqlite3
from pathlib import Path

from flashcards.database.connection import create_connection, initialize_database


def test_create_connection_returns_sqlite_connection(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)

    assert isinstance(connection, sqlite3.Connection)

    connection.close()


def test_create_connection_enables_foreign_keys(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"

    connection = create_connection(database_path)

    foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]

    assert foreign_keys_enabled == 1

    connection.close()


def test_initialize_database_creates_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)

    initialize_database(connection)

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()

    table_names = {row[0] for row in rows}

    assert "decks" in table_names
    assert "cards" in table_names
    assert "card_schedule" in table_names
    assert "review_events" in table_names

    connection.close()


def test_initialize_database_can_run_multiple_times(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)

    initialize_database(connection)
    initialize_database(connection)

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()

    table_names = {row[0] for row in rows}

    assert "decks" in table_names
    assert "cards" in table_names
    assert "card_schedule" in table_names
    assert "review_events" in table_names

    connection.close()
