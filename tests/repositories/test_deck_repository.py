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


def test_get_by_id_returns_deck(tmp_path):
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

    found_deck = repository.get_by_id(created_deck.id)

    assert found_deck is not None
    assert found_deck.id == created_deck.id
    assert found_deck.name == "Computer Science"
    assert found_deck.created_at == now
    assert found_deck.updated_at == now

    connection.close()


def test_get_by_id_returns_none_when_deck_does_not_exist(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = DeckRepository(connection)

    found_deck = repository.get_by_id(999)

    assert found_deck is None

    connection.close()


def test_get_all_returns_all_decks(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = DeckRepository(connection)

    now = datetime.now(UTC)

    first_deck = repository.create(
        Deck(
            id=None,
            name="Computer Science",
            created_at=now,
            updated_at=now,
        )
    )

    second_deck = repository.create(
        Deck(
            id=None,
            name="Mathematics",
            created_at=now,
            updated_at=now,
        )
    )

    decks = repository.get_all()

    assert decks == [first_deck, second_deck]

    connection.close()


def test_get_all_returns_empty_list_when_no_decks_exist(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = DeckRepository(connection)

    decks = repository.get_all()

    assert decks == []

    connection.close()
