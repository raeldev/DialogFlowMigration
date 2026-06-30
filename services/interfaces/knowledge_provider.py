from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IKnowledgeProvider(ABC):
    """
    Abstract interface for retrieving knowledge articles (Grounding/RAG).
    Ensures Clean Architecture Dependency Inversion Principle (DIP).
    """
    @abstractmethod
    def search_articles(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search knowledge base articles matching the user query.
        """
        pass
