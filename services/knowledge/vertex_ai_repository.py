import os
import json
import logging
from typing import List, Dict, Any, Optional
from services.interfaces.knowledge_provider import IKnowledgeProvider

logger = logging.getLogger("gecx.knowledge")

class VertexAISearchRepository(IKnowledgeProvider):
    """
    Google Cloud Discovery Engine (Vertex AI Search) implementation of IKnowledgeProvider.
    Enforces configurable CCaaS timeout SLA and structured error logging on search failure.
    """
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        data_store_id: Optional[str] = None
    ):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "")
        self.location = location or os.getenv("GCP_LOCATION", "global")
        self.data_store_id = data_store_id or os.getenv("GCP_DATA_STORE_ID", "")

    def search_articles(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Retrieve CCaaS timeout SLA threshold in seconds (default 4.0s to prevent drop calls)
        timeout_sec = float(os.getenv("GCP_RAG_TIMEOUT_SECONDS", "4.0"))

        if not self.project_id or not self.data_store_id:
            logger.warning(json.dumps({
                "event": "rag_search_skipped",
                "reason": "Missing GCP_PROJECT_ID or GCP_DATA_STORE_ID configuration",
                "query": query
            }))
            return []

        try:
            from google.cloud import discoveryengine_v1 as discoveryengine

            client = discoveryengine.SearchServiceClient()
            serving_config = client.serving_config_path(
                project=self.project_id,
                location=self.location,
                data_store=self.data_store_id,
                serving_config="default_serving_config",
            )

            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=limit,
            )

            response = client.search(request=request, timeout=timeout_sec)
            results = []
            for item in response.results:
                doc_dict = {}
                doc = item.document
                doc_dict["id"] = doc.id
                
                struct_data = doc.struct_data if hasattr(doc, "struct_data") else {}
                title = struct_data.get("title", "")
                content = struct_data.get("content", "")
                
                if not content and hasattr(doc, "derived_struct_data"):
                    snippets = doc.derived_struct_data.get("snippets", [])
                    if snippets and isinstance(snippets, list):
                        content = snippets[0].get("snippet", "")
                        title = title or snippets[0].get("title", f"Doc {doc.id}")

                doc_dict["title"] = title or f"Article {doc.id}"
                doc_dict["content"] = content or str(struct_data)
                results.append(doc_dict)

            logger.info(json.dumps({
                "event": "rag_search",
                "engine": "vertex_ai_search",
                "query": query,
                "results_count": len(results),
                "matched_ids": [r["id"] for r in results]
            }))
            return results[:limit]

        except Exception as exc:
            status_code = getattr(exc, "code", getattr(exc, "status_code", "UNKNOWN"))
            logger.error(json.dumps({
                "event": "rag_search_error",
                "engine": "vertex_ai_search",
                "query": query,
                "status_code": str(status_code),
                "error": str(exc),
                "timeout_sec": timeout_sec
            }))
            return []
