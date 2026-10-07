# Adaptive Flashcard Learning Architecture

## Overview

Adaptive Flashcard Learning is a fully local, single-user PySide6 desktop application.

V1 provides standard flashcard functionality backed by a hand-built spaced-repetition scheduler.

The architecture deliberately separates application workflows, persistence, user-interface code, and scheduling intelligence.

This separation is important because the long-term project goal is to experiment with and evaluate alternative learning algorithms without rewriting the rest of the application.

## Design Goals

The architecture should:

- remain understandable to a single developer
- keep V1 simple
- separate scheduling logic from persistence and UI code
- preserve raw review history for future analysis
- support deterministic testing of learning algorithms
- allow future schedulers to be compared
- operate entirely locally
- avoid unnecessary infrastructure

Future extensibility is important, but V1 should not contain abstractions for functionality that does not yet exist.

## Application Architecture

The conceptual architecture is:

```text
             PySide6 UI
                 │
                 ▼
        Application Services
            /           \
           ▼             ▼
   Repositories      Learning Engine
        │                  │
        ▼                  ▼
      SQLite       Rule-Based Scheduler
```

Plain Python domain objects move between these layers.

## Dependency Direction

Dependencies should generally move inward toward application/domain behavior rather than allowing low-level technologies to control the design.

Important boundaries include:

```text
UI → Services

Services → Repositories

Services → Learning Engine

Repositories → Database

Learning Engine → Domain concepts
```

The learning engine must not depend on repositories, SQLite, or PySide6.

The UI must not directly execute SQL or implement scheduling rules.

## UI Layer

Location:

```text
src/flashcards/ui/
```

The UI is implemented with PySide6.

V1 contains four primary views:

```text
Decks
  ↓
Deck Detail
├── Card Editor
└── Study
```

The UI is responsible for:

- rendering information
- collecting user input
- navigating between views
- notifying application services about user actions

It should contain presentation logic, not persistence or scheduling logic.

For example, the Study view may detect that the learner clicked `Good`, but it should not calculate the resulting interval.

## Application Services

Location:

```text
src/flashcards/services/
```

Application services coordinate use cases.

Examples include:

- creating a deck
- renaming a deck
- deleting a card
- retrieving due cards
- completing a review

Services connect the UI with repositories and the learning engine.

A service may coordinate several operations without implementing the underlying persistence or scheduling rules itself.

## Domain Models

Location:

```text
src/flashcards/domain/
```

Domain models are plain Python representations of important application concepts.

Likely V1 concepts include:

```text
Deck
Card
CardSchedule
ReviewEvent
Rating
CardState
```

Dataclasses are preferred where they make these structures clearer.

Domain objects should not know how to display themselves or persist themselves.

## Repository Layer

Location:

```text
src/flashcards/repositories/
```

Repositories isolate persistence operations from the rest of the application.

Examples include:

```text
retrieve all decks
retrieve cards belonging to a deck
retrieve new/due cards
create a card
update scheduling state
append a review event
```

Repositories communicate with SQLite and return application/domain data.

The application does not need abstract repository interfaces in V1 unless a concrete testing or design problem demonstrates a need for them.

## Database Layer

Location:

```text
src/flashcards/database/
```

The database layer contains SQLite-specific infrastructure such as:

- opening database connections
- enabling required SQLite behavior
- initializing the database
- creating the schema

SQLite is embedded in the application through Python's `sqlite3` module.

There is no database server.

Development data may be stored under:

```text
dev_data/
```

Released application data should eventually be placed in the appropriate per-user application-data directory for the operating system.

## Learning Engine

Location:

```text
src/flashcards/learning/
```

The learning engine contains scheduling intelligence.

V1 contains a rule-based scheduler.

Conceptually:

```text
current scheduling state
        +
rating
        +
reviewed_at
        │
        ▼
 RuleBasedScheduler
        │
        ▼
 scheduling decision
```

The scheduler determines the new scheduling state but does not persist it.

This makes scheduling behavior deterministic and independently testable.

## Scheduler Boundary

The scheduler should behave approximately like:

```text
schedule(current_state, rating, reviewed_at)
        ↓
new scheduling state
```

Its inputs contain the information necessary to make the scheduling decision.

Its output describes that decision.

The scheduler must not:

```text
read SQLite
write SQLite
execute SQL
render PySide6 widgets
navigate views
modify UI state
```

This separation creates an important extension point.

V1:

```text
StudyService
     │
     ▼
RuleBasedScheduler
```

A future version may support:

```text
StudyService
     │
     ├── RuleBasedScheduler
     │
     └── MLScheduler
```

without requiring the UI or persistence architecture to be rewritten.

## V1 Scheduling Model

Cards have two scheduling states:

```text
LEARNING
REVIEW
```

New cards begin in `LEARNING` and are immediately due.

### Learning State

```text
Again → 1 minute → LEARNING
Hard  → 1 day    → REVIEW
Good  → 2 days   → REVIEW
Easy  → 4 days   → REVIEW
```

### Review State

```text
Again → 1 minute               → LEARNING
Hard  → current interval × 1.2 → REVIEW
Good  → current interval × 2.0 → REVIEW
Easy  → current interval × 3.0 → REVIEW
```

For every review:

```text
due_at = reviewed_at + new interval

review_count += 1
```

For `Again`:

```text
failure_count += 1
```

Intervals are represented in integer seconds.

## Study Review Flow

A completed review crosses several architectural layers.

Conceptually:

```text
StudyView
    │
    │ rating
    │ response_time_ms
    ▼
StudyService
    │
    ├──────────────► Repository
    │                     │
    │                     ▼
    │              Current Schedule
    │
    ▼
RuleBasedScheduler
    │
    │ Scheduling Decision
    ▼
StudyService
    │
    ├──────────────► Update card_schedule
    │
    └──────────────► Append review_event
```

The service coordinates the operation.

The repository handles persistence.

The scheduler calculates the scheduling decision.

The UI initiates the operation and displays the result.

## Response-Time Measurement

Response time is measured as:

```text
card displayed
      ↓
 learner thinks
      ↓
answer revealed
```

The timer stops when the answer is revealed.

Time spent choosing:

```text
Again
Hard
Good
Easy
```

is not part of `response_time_ms`.

This distinction is important because response time may later become useful behavioral data for ML experiments.

## Data Model

V1 uses four conceptual tables.

### decks

Stores deck identity and metadata.

Approximate fields:

```text
id
name
created_at
updated_at
```

### cards

Stores flashcard content.

Approximate fields:

```text
id
deck_id
front
back
created_at
updated_at
```

Each card belongs to exactly one deck.

### card_schedule

Stores the current scheduling state of each card.

Approximate fields:

```text
card_id
state
due_at
interval_seconds
review_count
failure_count
```

Scheduling information is deliberately separated from card content.

### review_events

Stores historical review observations.

Approximate fields:

```text
id
card_id
reviewed_at
rating
response_time_ms
previous_state
new_state
previous_interval_seconds
new_interval_seconds
previous_due_at
new_due_at
```

Review events are append-only historical observations.

Completing a new review creates a new event rather than overwriting an earlier event.

## Why Separate Current State and History?

`card_schedule` answers:

> What is the scheduling state of this card right now?

`review_events` answers:

> What happened during previous reviews?

For example:

```text
card_schedule
─────────────
Card 42
REVIEW
due tomorrow
interval = 4 days
```

while:

```text
review_events
─────────────
Review 1 → Good
Review 2 → Good
Review 3 → Again
Review 4 → Good
...
```

The current schedule can change continuously while the historical observations remain preserved.

This is essential for future analysis and ML experiments.

## Raw Data Philosophy

V1 stores raw historical observations rather than prematurely creating an ML dataset.

For example, V1 stores:

```text
rating = AGAIN
```

rather than immediately converting it to:

```text
remembered = false
```

A future modeling experiment may define the target differently.

Likewise, V1 should not persist engineered values such as:

```text
historical accuracy
average response time
days since previous review
failure rate
estimated difficulty
```

Those values should be derived from historical data during feature engineering.

This preserves flexibility for later experiments.

## Future ML Integration

The intended long-term data flow is:

```text
review_events
      │
      ▼
Feature Engineering
      │
      ▼
Training Dataset
      │
      ▼
Memory Prediction Model
      │
      ▼
P(user remembers card)
      │
      ▼
ML-Based Scheduling
```

Potential features may eventually include:

```text
time since previous review
previous interval
previous ratings
historical success rate
failure count
response-time statistics
card-specific difficulty estimates
```

These features are not part of V1.

A likely early ML experiment is logistic regression predicting the probability that the learner remembers a card.

The rule-based V1 scheduler remains the baseline against which ML scheduling approaches can be evaluated.

## Testing Strategy

The architecture intentionally makes the learning engine easy to test independently.

For example:

```text
LEARNING + Again
→ LEARNING
→ 60-second interval
```

can be tested without:

- launching PySide6
- creating a real user database
- simulating mouse interaction

Scheduler tests should cover all state/rating combinations and relevant counter changes.

Repository tests should use isolated temporary SQLite databases.

Service tests should verify workflow coordination.

UI testing can be introduced when it provides sufficient value; extensive automated GUI testing is not required merely for architectural completeness.

## Simplicity Principle

This architecture is intentionally smaller than a typical enterprise architecture.

V1 does not require:

```text
microservices
HTTP APIs
dependency-injection frameworks
event buses
ORMs
container infrastructure
cloud services
```

Additional abstractions should be introduced when a concrete requirement justifies them, not because they might theoretically be useful later.

The architecture should remain easy enough for one developer to understand end-to-end.
