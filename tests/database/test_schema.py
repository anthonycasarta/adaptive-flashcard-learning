import sqlite3

from flashcards.database.schema import SCHEMA_STATEMENTS


def test_schema_creates_all_tables() -> None:
    connection = sqlite3.connect(":memory:")

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)

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


def test_review_events_has_expected_columns() -> None:
    connection = sqlite3.connect(":memory:")

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)

    rows = connection.execute("PRAGMA table_info(review_events)").fetchall()

    column_names = {row[1] for row in rows}

    assert column_names == {
        "id",
        "card_id",
        "reviewed_at",
        "rating",
        "response_time_ms",
        "previous_state",
        "new_state",
        "previous_interval_seconds",
        "new_interval_seconds",
        "previous_due_at",
        "new_due_at",
    }

    connection.close()


def test_schema_defines_expected_foreign_keys() -> None:
    connection = sqlite3.connect(":memory:")

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)

    cards_foreign_keys = connection.execute("PRAGMA foreign_key_list(cards)").fetchall()

    schedule_foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(card_schedule)"
    ).fetchall()

    review_foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(review_events)"
    ).fetchall()

    assert any(
        row[2] == "decks" and row[3] == "deck_id" and row[4] == "id"
        for row in cards_foreign_keys
    )

    assert any(
        row[2] == "cards" and row[3] == "card_id" and row[4] == "id"
        for row in schedule_foreign_keys
    )

    assert any(
        row[2] == "cards" and row[3] == "card_id" and row[4] == "id"
        for row in review_foreign_keys
    )

    connection.close()


def test_deleting_deck_cascades_to_cards_and_related_data() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)

    connection.execute(
        """
        INSERT INTO decks (id, name, created_at, updated_at)
        VALUES (1, 'Test Deck', '2026-10-07T12:00:00+00:00', '2026-10-07T12:00:00+00:00')
        """
    )

    connection.execute(
        """
        INSERT INTO cards (id, deck_id, front, back, created_at, updated_at)
        VALUES (
            1,
            1,
            'Front',
            'Back',
            '2026-10-07T12:00:00+00:00',
            '2026-10-07T12:00:00+00:00'
        )
        """
    )

    connection.execute(
        """
        INSERT INTO card_schedule (
            card_id,
            state,
            due_at,
            interval_seconds,
            review_count,
            failure_count
        )
        VALUES (
            1,
            'learning',
            '2026-10-07T12:00:00+00:00',
            0,
            0,
            0
        )
        """
    )

    connection.execute("DELETE FROM decks WHERE id = 1")

    card = connection.execute("SELECT * FROM cards WHERE id = 1").fetchone()

    schedule = connection.execute(
        "SELECT * FROM card_schedule WHERE card_id = 1"
    ).fetchone()

    assert card is None
    assert schedule is None

    connection.close()
