from datetime import UTC, datetime

from flashcards.domain.models import (
    Card,
    CardSchedule,
    CardState,
    Deck,
    Rating,
    ReviewEvent,
)


def test_card_state_values():
    assert CardState.LEARNING.value == "learning"
    assert CardState.REVIEW.value == "review"


def test_rating_values():
    assert Rating.AGAIN.value == "again"
    assert Rating.HARD.value == "hard"
    assert Rating.GOOD.value == "good"
    assert Rating.EASY.value == "easy"


def test_deck_creation():
    created_at = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)

    deck = Deck(
        id=1,
        name="Chemistry",
        created_at=created_at,
        updated_at=created_at,
    )

    assert deck.id == 1
    assert deck.name == "Chemistry"
    assert deck.created_at == created_at
    assert deck.updated_at == created_at


def test_card_creation():
    created_at = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)

    card = Card(
        id=1,
        deck_id=1,
        front="What is H2O?",
        back="Water",
        created_at=created_at,
        updated_at=created_at,
    )

    assert card.id == 1
    assert card.deck_id == 1
    assert card.front == "What is H2O?"
    assert card.back == "Water"
    assert card.created_at == created_at
    assert card.updated_at == created_at


def test_card_schedule_creation():
    due_at = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)

    schedule = CardSchedule(
        card_id=1,
        state=CardState.LEARNING,
        due_at=due_at,
        interval_seconds=0,
        review_count=0,
        failure_count=0,
    )

    assert schedule.card_id == 1
    assert schedule.state == CardState.LEARNING
    assert schedule.due_at == due_at
    assert schedule.interval_seconds == 0
    assert schedule.review_count == 0
    assert schedule.failure_count == 0


def test_review_event_creation():
    reviewed_at = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)
    previous_due_at = datetime(2026, 10, 7, 11, 0, tzinfo=UTC)
    new_due_at = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)

    review_event = ReviewEvent(
        id=1,
        card_id=1,
        reviewed_at=reviewed_at,
        rating=Rating.GOOD,
        response_time_ms=2500,
        previous_state=CardState.LEARNING,
        new_state=CardState.REVIEW,
        previous_interval_seconds=0,
        new_interval_seconds=172800,
        previous_due_at=previous_due_at,
        new_due_at=new_due_at,
    )

    assert review_event.id == 1
    assert review_event.card_id == 1
    assert review_event.reviewed_at == reviewed_at
    assert review_event.rating == Rating.GOOD
    assert review_event.response_time_ms == 2500
    assert review_event.previous_state == CardState.LEARNING
    assert review_event.new_state == CardState.REVIEW
    assert review_event.previous_interval_seconds == 0
    assert review_event.new_interval_seconds == 172800
    assert review_event.previous_due_at == previous_due_at
    assert review_event.new_due_at == new_due_at
