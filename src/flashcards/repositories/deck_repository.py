import sqlite3

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
