import sqlite3
from datetime import datetime

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

    def get_by_id(self, card_id: int) -> Card | None:
        row = self._connection.execute(
            """
            SELECT id, deck_id, front, back, created_at, updated_at
            FROM cards
            WHERE id = ?
            """,
            (card_id,),
        ).fetchone()

        if row is None:
            return None

        return Card(
            id=row[0],
            deck_id=row[1],
            front=row[2],
            back=row[3],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
        )
