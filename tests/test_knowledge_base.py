import pytest
from services.knowledge.in_memory_repository import InMemoryKnowledgeRepository

def test_search_articles_telecom():
    repo = InMemoryKnowledgeRepository()
    results = repo.search_articles("router blinking red light")
    assert len(results) > 0
    assert "KB-101" in [r["id"] for r in results]

def test_search_articles_billing():
    repo = InMemoryKnowledgeRepository()
    results = repo.search_articles("duplicate invoice charge")
    assert len(results) > 0
    assert "KB-102" in [r["id"] for r in results]

def test_search_articles_empty():
    repo = InMemoryKnowledgeRepository()
    results = repo.search_articles("extraterrestrial spaceship query")
    assert len(results) == 0
