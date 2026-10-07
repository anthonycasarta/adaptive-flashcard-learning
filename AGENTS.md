# AGENTS.md

## Project Purpose

Adaptive Flashcard Learning is a fully local desktop flashcard application.

The long-term goal is to investigate whether a learner's probability of remembering a flashcard can be predicted and used to improve review scheduling.

The project is also intended as a learning project for software engineering, data science, and machine learning.

The core learning system must be built and understood within the project rather than delegated to an external LLM or cloud service.

## Current Development Phase

The project is currently building V1.

V1 establishes:

- the desktop application
- local persistence
- review-history collection
- a hand-built rule-based spaced-repetition scheduler
- a baseline for future ML experiments

Do not implement future-version functionality unless explicitly requested.

Designing V1 so future ML work is possible does not mean implementing ML infrastructure during V1.

## V1 Scope

V1 supports:

- create, rename, and delete decks
- create, edit, and delete flashcards
- front/back cards
- view cards belonging to a deck
- study new and due cards
- reveal answers
- rate recall using Again, Hard, Good, or Easy
- rule-based spaced repetition
- persistent local storage
- append-only review history
- response-time measurement

New cards are immediately eligible for study.

Normal study sessions contain new and due cards rather than cycling arbitrarily through every card.

Response time is measured from:

```text
card displayed → answer revealed
```

Do not include time spent selecting Again, Hard, Good, or Easy.

## Locked Technology Stack

Use:

- Python
- PySide6
- SQLite through Python's standard-library `sqlite3`
- pytest
- `pyproject.toml`
- Git/GitHub

Do not introduce another technology without an explicit architectural reason and user approval.

## Local-Only Requirement

The application must operate entirely on the user's local machine.

The core application must not require:

- AWS
- Azure
- Google Cloud
- Firebase
- Supabase
- Databricks
- hosted databases
- hosted backends
- external APIs
- internet connectivity
- user accounts
- authentication
- synchronization services

User flashcards, review history, scheduling state, settings, and future model data must remain local.

Do not add networking to V1.

## Application Style

The application is:

> A single-user, cross-platform, single-window PySide6 desktop application.

The four primary V1 views are:

1. Decks
2. Deck Detail
3. Card Editor
4. Study

Conceptual navigation:

```text
Decks
  ↓
Deck Detail
├── Card Editor
└── Study
```

## Architecture

Use the following conceptual architecture:

```text
PySide6 UI
    │
    ▼
Application Services
   / \
  ▼   ▼
Repositories    Learning Engine
    │                 │
    ▼                 ▼
 SQLite       Rule-Based Scheduler
```

Use plain Python domain objects, preferably dataclasses where appropriate.

Prefer explicit dependency passing over dependency-injection frameworks.

Do not introduce microservices, event buses, containers, or other infrastructure that is unnecessary for a local desktop application.

## Layer Responsibilities

### UI

Location:

```text
src/flashcards/ui/
```

Responsibilities:

- PySide6 widgets and windows
- displaying application state
- collecting user input
- navigation
- forwarding user actions to application services

The UI must not:

- execute SQL
- contain scheduling rules
- directly manipulate database tables

### Application Services

Location:

```text
src/flashcards/services/
```

Responsibilities:

- coordinate application workflows
- connect UI operations with repositories and the learning engine
- orchestrate study/review operations

Services should coordinate behavior rather than contain persistence details or scheduling algorithms.

### Domain

Location:

```text
src/flashcards/domain/
```

Responsibilities:

- plain Python representations of core application concepts
- shared enums/value concepts where appropriate

Likely V1 concepts include:

- Deck
- Card
- CardSchedule
- ReviewEvent
- Rating
- CardState

Domain objects should not depend on PySide6 or SQLite.

### Repositories

Location:

```text
src/flashcards/repositories/
```

Responsibilities:

- persistence operations
- converting stored data into domain objects
- creating, reading, updating, and deleting persisted application data

SQL belongs in the persistence layer, not the UI or learning engine.

Do not introduce abstract repository interfaces merely for architectural purity.

Introduce abstractions only when they solve an actual problem.

### Database

Location:

```text
src/flashcards/database/
```

Responsibilities:

- SQLite connection management
- database initialization
- schema creation
- database-specific configuration

The released application should eventually store user data in the operating system's appropriate application-data directory.

Development databases may live under `dev_data/` and must not be committed.

### Learning Engine

Location:

```text
src/flashcards/learning/
```

Responsibilities:

- scheduling algorithms
- future learning-related intelligence

The V1 scheduler should behave approximately like a pure function:

```text
schedule(current_state, rating, reviewed_at)
        ↓
new scheduling state
```

The scheduler calculates a scheduling decision.

It does not persist that decision.

The scheduler must not depend on:

- SQLite
- repositories
- PySide6
- UI state

This boundary is important because future versions should be able to compare or replace:

```text
RuleBasedScheduler
```

with something such as:

```text
MLScheduler
```

without rewriting the rest of the application.

## Data Model

V1 uses four conceptual tables.

### decks

Contains approximately:

- id
- name
- created_at
- updated_at

### cards

Contains approximately:

- id
- deck_id
- front
- back
- created_at
- updated_at

Each card belongs to exactly one deck.

### card_schedule

Contains approximately:

- card_id
- state
- due_at
- interval_seconds
- review_count
- failure_count

Scheduling state must remain separate from card content.

### review_events

Contains approximately:

- id
- card_id
- reviewed_at
- rating
- response_time_ms
- previous_state
- new_state
- previous_interval_seconds
- new_interval_seconds
- previous_due_at
- new_due_at

Every completed review creates a new historical event.

Do not overwrite previous review events.

Exact SQL types, constraints, indexes, timestamp representation, and foreign-key behavior will be decided during database implementation.

## Review History Requirements

Review history should preserve raw observations that can later become an ML dataset.

Store the original four-level rating:

- Again
- Hard
- Good
- Easy

Do not store a derived `remembered` boolean in V1.

A future version may choose a definition such as:

```text
Again → not remembered
Hard/Good/Easy → remembered
```

but that decision must not be baked into the raw V1 data.

Store response time as integer milliseconds.

Store scheduling intervals as integer seconds.

Do not prematurely store engineered features such as:

- historical accuracy
- average response time
- days since previous review
- failure rate
- estimated difficulty
- remembered/not-remembered labels

Those should later be derived from raw historical data.

## V1 Scheduler Rules

Cards have two states:

```text
LEARNING
REVIEW
```

New cards begin in `LEARNING` and are immediately due.

### LEARNING

Again:

```text
interval = 60 seconds
state = LEARNING
```

Hard:

```text
interval = 1 day
state = REVIEW
```

Good:

```text
interval = 2 days
state = REVIEW
```

Easy:

```text
interval = 4 days
state = REVIEW
```

### REVIEW

Again:

```text
interval = 60 seconds
state = LEARNING
```

Hard:

```text
interval = current interval × 1.2
state = REVIEW
```

Good:

```text
interval = current interval × 2.0
state = REVIEW
```

Easy:

```text
interval = current interval × 3.0
state = REVIEW
```

Calculate:

```text
due_at = reviewed_at + new interval
```

Every completed review increments:

```text
review_count += 1
```

Again additionally increments:

```text
failure_count += 1
```

Do not introduce an ease factor in V1.

An established card receiving Again effectively restarts its progression.

Example:

```text
12 days
  ↓ Again
1 minute
  ↓ Good
2 days
  ↓ Good
4 days
```

## Testing Expectations

Use pytest.

The learning engine should receive particularly strong unit-test coverage because scheduling behavior should be deterministic.

Tests should cover every meaningful state/rating transition.

Repository tests should use temporary/test SQLite databases rather than the user's real application database.

Tests must not require:

- internet access
- cloud services
- external databases

Prefer testing behavior rather than implementation details.

## Coding Guidelines

Keep implementations straightforward and readable.

Prefer:

- small focused modules
- explicit dependencies
- plain Python objects
- type hints where useful
- clear names
- deterministic business logic
- standard-library functionality when sufficient

Avoid abstractions that exist only because they are common in large production systems.

Do not create generic `utils` modules as dumping grounds for unrelated functionality.

Do not prematurely optimize.

Do not prematurely design infrastructure for hypothetical future requirements.

## Do Not Introduce

Unless explicitly requested, do not introduce:

- React
- JavaScript frontends
- FastAPI
- Flask
- Django
- HTTP APIs
- backend servers
- ORMs
- dependency-injection frameworks
- Docker
- microservices
- event buses
- cloud infrastructure
- telemetry
- analytics services
- accounts/authentication
- networking
- LLM APIs
- local LLMs
- embeddings
- ML frameworks
- ML models
- feature-engineering pipelines

## Future ML Direction

The expected long-term progression is:

```text
SQLite review history
        ↓
feature engineering
        ↓
training dataset
        ↓
memory prediction model
        ↓
P(user remembers card)
        ↓
ML-based scheduler
```

Potential future features may include:

- time since previous review
- historical accuracy
- failure rate
- previous ratings
- response-time statistics
- estimated card difficulty

These should be derived from historical observations when the ML phase begins.

Do not implement them in V1.

The V1 rule-based scheduler should remain available as a baseline for evaluating future scheduling approaches.

## Agent Workflow

When making changes:

1. Read this file and relevant documentation before modifying architecture.
2. Stay within the currently requested development step.
3. Do not implement future roadmap features unless explicitly requested.
4. Preserve layer boundaries.
5. Keep changes as small as reasonably possible.
6. Add or update tests when behavior changes.
7. Run relevant tests before considering work complete.
8. Do not silently introduce new dependencies.
9. Do not change locked architectural decisions without discussing the reason first.
10. Prefer the simplest implementation that satisfies the current requirement.

If a requested implementation appears to conflict with a locked project decision, identify the conflict rather than silently redesigning the application.
