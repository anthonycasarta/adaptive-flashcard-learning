from datetime import UTC, datetime

from flashcards.database.connection import create_connection, initialize_database
from flashcards.domain.models import Deck
from flashcards.repositories.deck_repository import DeckRepository


def test_create_deck(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = DeckRepository(connection)

    now = datetime.now(UTC)
    deck = Deck(
        id=None,
        name="Computer Science",
        created_at=now,
        updated_at=now,
    )

    created_deck = repository.create(deck)

    assert created_deck.id is not None
    assert created_deck.name == "Computer Science"
    assert created_deck.created_at == now
    assert created_deck.updated_at == now

    row = connection.execute(
        """
        SELECT id, name, created_at, updated_at
        FROM decks
        WHERE id = ?
        """,
        (created_deck.id,),
    ).fetchone()

    assert row is not None
    assert row[0] == created_deck.id
    assert row[1] == "Computer Science"
    assert row[2] == now.isoformat()
    assert row[3] == now.isoformat()

    connection.close()


def test_create_decks_generates_unique_ids(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = DeckRepository(connection)

    now = datetime.now(UTC)

    first_deck = Deck(
        id=None,
        name="Computer Science",
        created_at=now,
        updated_at=now,
    )

    second_deck = Deck(
        id=None,
        name="Mathematics",
        created_at=now,
        updated_at=now,
    )

    created_first = repository.create(first_deck)
    created_second = repository.create(second_deck)

    assert created_first.id is not None
    assert created_second.id is not None
    assert created_first.id != created_second.id

    connection.close()
