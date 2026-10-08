import sqlite3
from datetime import UTC, datetime, timedelta

import pytest

from flashcards.database.connection import create_connection, initialize_database
from flashcards.domain.models import Card, CardSchedule, CardState, Deck
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


def test_get_by_deck_id_returns_only_cards_for_deck(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    deck_repository = DeckRepository(connection)
    card_repository = CardRepository(connection)

    now = datetime.now(UTC)

    first_deck = deck_repository.create(
        Deck(
            id=None,
            name="Computer Science",
            created_at=now,
            updated_at=now,
        )
    )

    second_deck = deck_repository.create(
        Deck(
            id=None,
            name="Mathematics",
            created_at=now,
            updated_at=now,
        )
    )

    assert first_deck.id is not None
    assert second_deck.id is not None

    first_card = card_repository.create(
        Card(
            id=None,
            deck_id=first_deck.id,
            front="What is a stack?",
            back="A last-in, first-out data structure.",
            created_at=now,
            updated_at=now,
        )
    )

    second_card = card_repository.create(
        Card(
            id=None,
            deck_id=first_deck.id,
            front="What is a queue?",
            back="A first-in, first-out data structure.",
            created_at=now,
            updated_at=now,
        )
    )

    card_repository.create(
        Card(
            id=None,
            deck_id=second_deck.id,
            front="What is a derivative?",
            back="The instantaneous rate of change.",
            created_at=now,
            updated_at=now,
        )
    )

    cards = card_repository.get_by_deck_id(first_deck.id)

    assert cards == [first_card, second_card]

    connection.close()


def test_get_by_deck_id_returns_empty_list_when_deck_has_no_cards(tmp_path):
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

    cards = card_repository.get_by_deck_id(created_deck.id)

    assert cards == []

    connection.close()


def test_update_card(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    deck_repository = DeckRepository(connection)
    card_repository = CardRepository(connection)

    created_at = datetime.now(UTC)

    first_deck = deck_repository.create(
        Deck(
            id=None,
            name="Computer Science",
            created_at=created_at,
            updated_at=created_at,
        )
    )

    second_deck = deck_repository.create(
        Deck(
            id=None,
            name="Algorithms",
            created_at=created_at,
            updated_at=created_at,
        )
    )

    assert first_deck.id is not None
    assert second_deck.id is not None

    created_card = card_repository.create(
        Card(
            id=None,
            deck_id=first_deck.id,
            front="What is Big O?",
            back="A way to describe algorithm complexity.",
            created_at=created_at,
            updated_at=created_at,
        )
    )

    assert created_card.id is not None

    updated_at = datetime.now(UTC)

    updated_card = Card(
        id=created_card.id,
        deck_id=second_deck.id,
        front="What is Big-O notation?",
        back="A notation used to describe asymptotic complexity.",
        created_at=created_card.created_at,
        updated_at=updated_at,
    )

    card_repository.update(updated_card)

    found_card = card_repository.get_by_id(created_card.id)

    assert found_card is not None
    assert found_card.deck_id == second_deck.id
    assert found_card.front == "What is Big-O notation?"
    assert found_card.back == "A notation used to describe asymptotic complexity."
    assert found_card.created_at == created_at
    assert found_card.updated_at == updated_at

    connection.close()


def test_update_card_without_id_raises_value_error(tmp_path):
    database_path = tmp_path / "test.db"
    connection = create_connection(database_path)
    initialize_database(connection)

    repository = CardRepository(connection)

    now = datetime.now(UTC)

    card = Card(
        id=None,
        deck_id=1,
        front="Question",
        back="Answer",
        created_at=now,
        updated_at=now,
    )

    with pytest.raises(ValueError, match="Cannot update a card without an ID"):
        repository.update(card)

    connection.close()


def test_delete_card(tmp_path):
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

    card_repository.delete(created_card.id)

    found_card = card_repository.get_by_id(created_card.id)

    assert found_card is None

    connection.close()


def test_create_schedule(tmp_path):
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

    schedule = CardSchedule(
        card_id=created_card.id,
        state=CardState.LEARNING,
        due_at=now,
        interval_seconds=0,
        review_count=0,
        failure_count=0,
    )

    card_repository.create_schedule(schedule)

    row = connection.execute(
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
        (created_card.id,),
    ).fetchone()

    assert row is not None
    assert row[0] == created_card.id
    assert row[1] == "learning"
    assert row[2] == now.isoformat()
    assert row[3] == 0
    assert row[4] == 0
    assert row[5] == 0

    connection.close()


def test_get_schedule_returns_schedule(tmp_path):
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

    schedule = CardSchedule(
        card_id=created_card.id,
        state=CardState.LEARNING,
        due_at=now,
        interval_seconds=0,
        review_count=0,
        failure_count=0,
    )

    card_repository.create_schedule(schedule)

    found_schedule = card_repository.get_schedule(created_card.id)

    assert found_schedule is not None
    assert found_schedule == schedule

    connection.close()


def test_get_schedule_returns_none_when_schedule_does_not_exist(tmp_path):
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

    found_schedule = card_repository.get_schedule(created_card.id)

    assert found_schedule is None

    connection.close()


def test_update_schedule(tmp_path):
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

    initial_schedule = CardSchedule(
        card_id=created_card.id,
        state=CardState.LEARNING,
        due_at=now,
        interval_seconds=0,
        review_count=0,
        failure_count=0,
    )

    card_repository.create_schedule(initial_schedule)

    updated_schedule = CardSchedule(
        card_id=created_card.id,
        state=CardState.REVIEW,
        due_at=now + timedelta(days=2),
        interval_seconds=172800,
        review_count=1,
        failure_count=0,
    )

    card_repository.update_schedule(updated_schedule)

    found_schedule = card_repository.get_schedule(created_card.id)

    assert found_schedule is not None
    assert found_schedule == updated_schedule

    connection.close()


def test_create_with_schedule(tmp_path):
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

    created_card, created_schedule = card_repository.create_with_schedule(
        card=card,
        state=CardState.LEARNING,
        due_at=now,
        interval_seconds=0,
        review_count=0,
        failure_count=0,
    )

    assert created_card.id is not None
    assert created_schedule.card_id == created_card.id

    found_card = card_repository.get_by_id(created_card.id)
    found_schedule = card_repository.get_schedule(created_card.id)

    assert found_card == created_card
    assert found_schedule == created_schedule

    connection.close()


def test_create_with_schedule_rolls_back_when_schedule_insert_fails(tmp_path):
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

    connection.execute(
        """
        CREATE TRIGGER fail_schedule_insert
        BEFORE INSERT ON card_schedule
        BEGIN
            SELECT RAISE(ABORT, 'schedule insert failed');
        END;
        """
    )
    connection.commit()

    card = Card(
        id=None,
        deck_id=created_deck.id,
        front="What is a stack?",
        back="A last-in, first-out data structure.",
        created_at=now,
        updated_at=now,
    )

    with pytest.raises(sqlite3.IntegrityError, match="schedule insert failed"):
        card_repository.create_with_schedule(
            card=card,
            state=CardState.LEARNING,
            due_at=now,
            interval_seconds=0,
            review_count=0,
            failure_count=0,
        )

    rows = connection.execute(
        """
        SELECT id
        FROM cards
        WHERE deck_id = ?
        """,
        (created_deck.id,),
    ).fetchall()

    assert rows == []

    connection.close()
