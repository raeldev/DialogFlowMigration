from abc import ABC, abstractmethod
from typing import Dict, Any

class IAgentProvider(ABC):
    """
    Abstract interface for conversational agent orchestration.
    Ensures Clean Architecture Dependency Inversion Principle (DIP).
    """
    @abstractmethod
    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process a user message within a session, executing RAG and tools as needed.
        Returns dictionary containing reply, latency_ms, and tools_executed.
        """
        pass
