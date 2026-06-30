import json
import logging
from typing import List, Dict, Any
from services.interfaces.knowledge_provider import IKnowledgeProvider

logger = logging.getLogger("gecx.knowledge")

class InMemoryKnowledgeRepository(IKnowledgeProvider):
    """
    In-memory implementation of IKnowledgeProvider for RAG grounding.
    Provides mock articles for Apex Telecom & Financial Services.
    """
    def __init__(self):
        self._articles = [
            {
                "id": "KB-101",
                "title": "Telecom Wi-Fi Troubleshooting Guide",
                "content": "If internet connection drops or router shows blinking red optical light, run fiber network diagnostic check. If packet loss exceeds 10%, schedule on-site technician repair."
            },
            {
                "id": "KB-102",
                "title": "FinTech Billing & Invoice Policy",
                "content": "Invoices are issued on the 1st of each month. If a customer reports duplicate charges, verify payment status via CRM before processing refund."
            },
            {
                "id": "KB-103",
                "title": "Contract Cancellation & Termination Fee Policy",
                "content": "Contracts under 12 months incur a proportional early termination fee of R$ 150.00. For contracts over 12 months, cancellation is penalty-free."
            }
        ]

    def search_articles(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        results = []
        for art in self._articles:
            if any(term in art["content"].lower() or term in art["title"].lower() for term in query_lower.split()):
                results.append(art)
                if len(results) >= limit:
                    break
        
        logger.info(json.dumps({
            "event": "rag_search",
            "query": query,
            "results_count": len(results),
            "matched_ids": [r["id"] for r in results]
        }))
        return results
