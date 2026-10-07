DECKS_TABLE = """
CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

CARDS_TABLE = """
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    deck_id INTEGER NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);
"""

CARD_SCHEDULE_TABLE = """
CREATE TABLE IF NOT EXISTS card_schedule (
    card_id INTEGER PRIMARY KEY,
    state TEXT NOT NULL,
    due_at TEXT NOT NULL,
    interval_seconds INTEGER NOT NULL,
    review_count INTEGER NOT NULL,
    failure_count INTEGER NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
"""

REVIEW_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS review_events (
    id INTEGER PRIMARY KEY,
    card_id INTEGER NOT NULL,
    reviewed_at TEXT NOT NULL,
    rating TEXT NOT NULL,
    response_time_ms INTEGER NOT NULL,
    previous_state TEXT NOT NULL,
    new_state TEXT NOT NULL,
    previous_interval_seconds INTEGER NOT NULL,
    new_interval_seconds INTEGER NOT NULL,
    previous_due_at TEXT NOT NULL,
    new_due_at TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
"""

SCHEMA_STATEMENTS = (
    DECKS_TABLE,
    CARDS_TABLE,
    CARD_SCHEDULE_TABLE,
    REVIEW_EVENTS_TABLE,
)
