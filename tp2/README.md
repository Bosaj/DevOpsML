# TP2 - Tests avec Pytest

Ce projet contient les exercices du TP2 sur les tests en Python.

## Structure

- `src/` - Code source
  - `Ex1.py` - Opérations mathématiques (addition, soustraction, multiplication, division)
  - `Ex2.py` - Suppression de doublons consécutifs

- `tests/` - Tests
  - `unit/` - Tests unitaires
  - `integration/` - Tests d'intégration
  - `functional/` - Tests fonctionnels Flask

## Installation

poetry install

text

## Exécution des tests

Tous les tests
poetry run pytest

Tests unitaires seulement
poetry run pytest tests/unit/

Avec couverture
poetry run pytest --cov=src --cov-report=html

text

## Couverture

Le rapport de couverture HTML est généré dans `htmlcov/