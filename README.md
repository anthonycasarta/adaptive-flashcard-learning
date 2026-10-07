# Adaptive Flashcard Learning

A fully local desktop flashcard application designed to explore how spaced-repetition scheduling can evolve from hand-built rules into a personalized machine-learning system.

## Overview

Adaptive Flashcard Learning is a single-user desktop application for creating flashcard decks, studying cards, and scheduling reviews using spaced repetition.

The project is intentionally being developed in stages.

V1 uses a hand-built rule-based spaced-repetition scheduler. Later versions will use the review history collected by the application to explore feature engineering, memory prediction, personalization, and machine-learning-based scheduling.

The long-term research question behind the project is:

> Can I predict when a learner is about to forget a flashcard and schedule the review before that happens?

The goal is to build and understand the learning algorithms and machine-learning models used by the application rather than making the project an LLM wrapper.

## Project Goals

The project is intended to develop practical experience with:

- software architecture
- desktop application development
- relational databases
- data collection and modeling
- spaced-repetition algorithms
- feature engineering
- machine learning
- model evaluation
- personalized learning systems

The intelligence behind the core scheduling system will progressively be built and evaluated within the project.

## Local-First Design

Adaptive Flashcard Learning is designed to operate entirely on the user's computer.

The core application must not require:

- cloud infrastructure
- hosted databases
- hosted backends
- external APIs
- user accounts
- an internet connection

Flashcards, review history, scheduling information, settings, and future model data remain local.

SQLite is used for persistent application data.

## V1

V1 establishes the application and the baseline learning system that future ML approaches will be compared against.

V1 supports:

- creating, renaming, and deleting decks
- creating, editing, and deleting flashcards
- front/back flashcards
- viewing cards belonging to a deck
- studying new and due cards
- revealing answers
- rating recall as Again, Hard, Good, or Easy
- rule-based spaced repetition
- persistent local storage
- append-only review history
- response-time measurement

V1 intentionally does not include:

- machine learning
- LLM functionality
- embeddings
- analytics dashboards
- accounts or authentication
- synchronization
- networking
- cloud services
- rich text
- images or audio
- tags
- import/export

## Technology Stack

V1 uses:

- Python
- PySide6
- SQLite through Python's `sqlite3`
- pytest
- `pyproject.toml`
- Git and GitHub

The application is a single-user, cross-platform, single-window desktop application.

## Learning System

The learning system is intentionally being developed incrementally.

```text
V1 rule-based scheduler
        ↓
Raw review history
        ↓
Feature engineering
        ↓
Memory prediction model
        ↓
P(user remembers card)
        ↓
ML-based scheduling
```

V1 therefore serves two purposes:

1. provide a usable spaced-repetition system
2. establish a baseline against which future ML schedulers can be evaluated

## V1 Scheduler

Cards have two scheduling states:

- `LEARNING`
- `REVIEW`

New cards begin in `LEARNING` and are immediately eligible for study.

### Learning

| Rating | Next interval | New state |
|---|---:|---|
| Again | 1 minute | LEARNING |
| Hard | 1 day | REVIEW |
| Good | 2 days | REVIEW |
| Easy | 4 days | REVIEW |

### Review

| Rating | Next interval | New state |
|---|---:|---|
| Again | 1 minute | LEARNING |
| Hard | current interval × 1.2 | REVIEW |
| Good | current interval × 2.0 | REVIEW |
| Easy | current interval × 3.0 | REVIEW |

Every completed review increments the card's review count.

An `Again` rating also increments its failure count.

The next due time is calculated from:

```text
reviewed_at + new interval
```

## Architecture

The application uses a small layered architecture:

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

The major design rule is separation of responsibilities.

The UI does not contain SQL or scheduling rules.

Repositories handle persistence.

Application services coordinate application workflows.

The learning engine contains scheduling intelligence.

The scheduler does not know that SQLite or PySide6 exists.

See `docs/architecture.md` for the detailed architecture.

## Project Structure

```text
adaptive-flashcard-learning/
│
├── src/
│   └── flashcards/
│       ├── ui/
│       ├── services/
│       ├── domain/
│       ├── repositories/
│       ├── database/
│       ├── learning/
│       └── main.py
│
├── tests/
│   ├── domain/
│   ├── learning/
│   ├── repositories/
│   └── services/
│
├── docs/
│   └── architecture.md
│
├── dev_data/
│
├── .gitignore
├── AGENTS.md
├── pyproject.toml
├── README.md
└── LICENSE
```

## Development Status

The project is currently in the initial V1 development phase.

Requirements, architecture, data design, scheduling behavior, and repository structure have been defined.

Application implementation has not yet begun.

## Setup

Development-environment setup instructions will be added once project initialization is completed.

## Running the Application

Run instructions will be added once the initial application entry point exists.

## Running Tests

Testing instructions will be added once the Python project and pytest configuration are initialized.

## Future Direction

Future versions are expected to progressively introduce:

- review analytics
- feature engineering
- logistic regression
- prediction of recall probability
- ML-based scheduling
- learner personalization
- local NLP/free-response grading
- local embeddings
- potentially optional local LLM functionality

These features are intentionally excluded from V1.

Future ML systems should be evaluated against the V1 rule-based scheduler rather than replacing it without comparison.
