from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CardState(Enum):
    LEARNING = "learning"
    REVIEW = "review"


class Rating(Enum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


@dataclass
class Deck:
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Card:
    id: int
    deck_id: int
    front: str
    back: str
    created_at: datetime
    updated_at: datetime


@dataclass
class CardSchedule:
    card_id: int
    state: CardState
    due_at: datetime
    interval_seconds: int
    review_count: int
    failure_count: int


@dataclass
class ReviewEvent:
    id: int
    card_id: int
    reviewed_at: datetime
    rating: Rating
    response_time_ms: int
    previous_state: CardState
    new_state: CardState
    previous_interval_seconds: int
    new_interval_seconds: int
    previous_due_at: datetime
    new_due_at: datetime
