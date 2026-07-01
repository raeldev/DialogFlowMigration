import os
import logging
from unittest.mock import patch, MagicMock
from services.telemetry.gcp_logger import setup_gcp_telemetry

def test_setup_gcp_telemetry_disabled(monkeypatch):
    monkeypatch.setenv("USE_REAL_GCP", "false")
    res = setup_gcp_telemetry()
    assert res is False

@patch("google.cloud.logging.Client")
@patch("google.cloud.logging.handlers.CloudLoggingHandler")
@patch("google.cloud.logging_v2.handlers.transports.BackgroundThreadTransport")
def test_setup_gcp_telemetry_enabled_mock(mock_transport, mock_handler, mock_client, monkeypatch):
    monkeypatch.setenv("USE_REAL_GCP", "true")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-gcp-project")
    
    mock_client_inst = MagicMock()
    mock_client.return_value = mock_client_inst
    
    mock_handler_inst = MagicMock()
    mock_handler_inst.level = logging.INFO
    mock_handler.return_value = mock_handler_inst
    
    root_logger = logging.getLogger("gecx")
    initial_handlers = list(root_logger.handlers)
    
    try:
        res = setup_gcp_telemetry()
        assert res is True
        mock_client.assert_called_once_with(project="test-gcp-project")
        mock_transport.assert_called_once_with(mock_client_inst, name="gecx-worker")
    finally:
        root_logger.handlers = initial_handlers
