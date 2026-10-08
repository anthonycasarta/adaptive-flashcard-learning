import sqlite3

from flashcards.domain.models import Card


class CardRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, card: Card) -> Card:
        cursor = self._connection.execute(
            """
            INSERT INTO cards (deck_id, front, back, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                card.deck_id,
                card.front,
                card.back,
                card.created_at.isoformat(),
                card.updated_at.isoformat(),
            ),
        )

        self._connection.commit()

        return Card(
            id=cursor.lastrowid,
            deck_id=card.deck_id,
            front=card.front,
            back=card.back,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )
