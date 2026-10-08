import sqlite3
from datetime import UTC, datetime

import pytest

from flashcards.database.connection import create_connection, initialize_database
from flashcards.domain.models import Card, Deck
from flashcards.repositories.card_repository import CardRepository
from flashcards.repositories.deck_repository import DeckRepository


def test_create_card(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    deck_repository = DeckRepository(connection)
    card_repository = CardRepository(connection)

    now = datetime.now(UTC)

    created_deck = deck_repository.create(
        Deck(
            id=None,
            name="Computer Science",
            created_at=now,
            updated_at=now,
        )
    )

    assert created_deck.id is not None

    card = Card(
        id=None,
        deck_id=created_deck.id,
        front="What is a stack?",
        back="A last-in, first-out data structure.",
        created_at=now,
        updated_at=now,
    )

    created_card = card_repository.create(card)

    assert created_card.id is not None
    assert created_card.deck_id == created_deck.id
    assert created_card.front == "What is a stack?"
    assert created_card.back == "A last-in, first-out data structure."
    assert created_card.created_at == now
    assert created_card.updated_at == now

    row = connection.execute(
        """
        SELECT id, deck_id, front, back, created_at, updated_at
        FROM cards
        WHERE id = ?
        """,
        (created_card.id,),
    ).fetchone()

    assert row is not None
    assert row[0] == created_card.id
    assert row[1] == created_deck.id
    assert row[2] == "What is a stack?"
    assert row[3] == "A last-in, first-out data structure."
    assert row[4] == now.isoformat()
    assert row[5] == now.isoformat()

    connection.close()


def test_create_card_with_nonexistent_deck_raises_integrity_error(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = CardRepository(connection)

    now = datetime.now(UTC)

    card = Card(
        id=None,
        deck_id=999,
        front="What is a queue?",
        back="A first-in, first-out data structure.",
        created_at=now,
        updated_at=now,
    )

    with pytest.raises(sqlite3.IntegrityError):
        repository.create(card)

    connection.close()


def test_get_by_id_returns_card(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    deck_repository = DeckRepository(connection)
    card_repository = CardRepository(connection)

    now = datetime.now(UTC)

    created_deck = deck_repository.create(
        Deck(
            id=None,
            name="Computer Science",
            created_at=now,
            updated_at=now,
        )
    )

    assert created_deck.id is not None

    created_card = card_repository.create(
        Card(
            id=None,
            deck_id=created_deck.id,
            front="What is a stack?",
            back="A last-in, first-out data structure.",
            created_at=now,
            updated_at=now,
        )
    )

    assert created_card.id is not None

    found_card = card_repository.get_by_id(created_card.id)

    assert found_card is not None
    assert found_card == created_card

    connection.close()


def test_get_by_id_returns_none_when_card_does_not_exist(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = CardRepository(connection)

    found_card = repository.get_by_id(999)

    assert found_card is None

    connection.close()
