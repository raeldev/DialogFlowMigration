import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("gecx.telemetry")

def setup_gcp_telemetry(project_id: Optional[str] = None) -> bool:
    """
    Configures Python logging to emit structured JSON logs directly to Google Cloud Logging
    using non-blocking BackgroundThreadTransport when USE_REAL_GCP='true'.
    Returns True if remote GCP logging was successfully attached, False otherwise.
    """
    use_gcp = os.getenv("USE_REAL_GCP", "").lower() in ("true", "1", "yes")
    if not use_gcp:
        logger.info(json.dumps({
            "event": "telemetry_setup",
            "mode": "local_stream",
            "message": "USE_REAL_GCP is disabled. Using local stdout JSON stream logging."
        }))
        return False

    try:
        from google.cloud import logging as cloud_logging
        from google.cloud.logging.handlers import CloudLoggingHandler
        from google.cloud.logging_v2.handlers.transports import BackgroundThreadTransport

        target_project = project_id or os.getenv("GCP_PROJECT_ID")
        client = cloud_logging.Client(project=target_project)
        
        # Explicitly configure non-blocking background transport
        transport = BackgroundThreadTransport(client, name="gecx-worker")
        handler = CloudLoggingHandler(client, name="gecx-agent-poc", transport=transport)
        
        root_logger = logging.getLogger("gecx")
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        logger.info(json.dumps({
            "event": "telemetry_setup",
            "mode": "gcp_cloud_logging",
            "project_id": target_project,
            "transport": "BackgroundThreadTransport"
        }))
        return True
    except Exception as exc:
        logger.warning(json.dumps({
            "event": "telemetry_setup_failed",
            "mode": "fallback_local",
            "error": str(exc)
        }))
        return False
