import sqlite3
from datetime import datetime

from flashcards.domain.models import Deck


class DeckRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, deck: Deck) -> Deck:
        cursor = self._connection.execute(
            """
            INSERT INTO decks (name, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (
                deck.name,
                deck.created_at.isoformat(),
                deck.updated_at.isoformat(),
            ),
        )

        self._connection.commit()

        return Deck(
            id=cursor.lastrowid,
            name=deck.name,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
        )

    def get_by_id(self, deck_id: int) -> Deck | None:
        row = self._connection.execute(
            """
            SELECT id, name, created_at, updated_at
            FROM decks
            WHERE id = ?
            """,
            (deck_id,),
        ).fetchone()

        if row is None:
            return None

        return Deck(
            id=row[0],
            name=row[1],
            created_at=datetime.fromisoformat(row[2]),
            updated_at=datetime.fromisoformat(row[3]),
        )

    def get_all(self) -> list[Deck]:
        rows = self._connection.execute(
            """
            SELECT id, name, created_at, updated_at
            FROM decks
            ORDER BY id
            """
        ).fetchall()

        return [
            Deck(
                id=row[0],
                name=row[1],
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3]),
            )
            for row in rows
        ]

    def update(self, deck: Deck) -> None:
        if deck.id is None:
            raise ValueError("Cannot update a deck without an ID")

        self._connection.execute(
            """
            UPDATE decks
            SET name = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                deck.name,
                deck.updated_at.isoformat(),
                deck.id,
            ),
        )

        self._connection.commit()
