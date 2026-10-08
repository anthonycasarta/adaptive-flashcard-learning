import sqlite3
from datetime import datetime

from flashcards.domain.models import Card, CardSchedule, CardState


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

    def get_by_deck_id(self, deck_id: int) -> list[Card]:
        rows = self._connection.execute(
            """
            SELECT id, deck_id, front, back, created_at, updated_at
            FROM cards
            WHERE deck_id = ?
            ORDER BY id
            """,
            (deck_id,),
        ).fetchall()

        return [
            Card(
                id=row[0],
                deck_id=row[1],
                front=row[2],
                back=row[3],
                created_at=datetime.fromisoformat(row[4]),
                updated_at=datetime.fromisoformat(row[5]),
            )
            for row in rows
        ]

    def update(self, card: Card) -> None:
        if card.id is None:
            raise ValueError("Cannot update a card without an ID")

        self._connection.execute(
            """
            UPDATE cards
            SET deck_id = ?, front = ?, back = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                card.deck_id,
                card.front,
                card.back,
                card.updated_at.isoformat(),
                card.id,
            ),
        )

        self._connection.commit()

    def delete(self, card_id: int) -> None:
        self._connection.execute(
            """
            DELETE FROM cards
            WHERE id = ?
            """,
            (card_id,),
        )

        self._connection.commit()

    def create_schedule(self, schedule: CardSchedule) -> None:
        self._connection.execute(
            """
            INSERT INTO card_schedule (
                card_id,
                state,
                due_at,
                interval_seconds,
                review_count,
                failure_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                schedule.card_id,
                schedule.state.value,
                schedule.due_at.isoformat(),
                schedule.interval_seconds,
                schedule.review_count,
                schedule.failure_count,
            ),
        )

        self._connection.commit()

    def get_schedule(self, card_id: int) -> CardSchedule | None:
        row = self._connection.execute(
            """
            SELECT
                card_id,
                state,
                due_at,
                interval_seconds,
                review_count,
                failure_count
            FROM card_schedule
            WHERE card_id = ?
            """,
            (card_id,),
        ).fetchone()

        if row is None:
            return None

        return CardSchedule(
            card_id=row[0],
            state=CardState(row[1]),
            due_at=datetime.fromisoformat(row[2]),
            interval_seconds=row[3],
            review_count=row[4],
            failure_count=row[5],
        )

    def update_schedule(self, schedule: CardSchedule) -> None:
        self._connection.execute(
            """
            UPDATE card_schedule
            SET
                state = ?,
                due_at = ?,
                interval_seconds = ?,
                review_count = ?,
                failure_count = ?
            WHERE card_id = ?
            """,
            (
                schedule.state.value,
                schedule.due_at.isoformat(),
                schedule.interval_seconds,
                schedule.review_count,
                schedule.failure_count,
                schedule.card_id,
            ),
        )

        self._connection.commit()
