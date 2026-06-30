from services.tools.crm_tools import get_invoice_status, run_network_diagnostic, open_support_ticket, AVAILABLE_TOOLS

def test_get_invoice_status():
    res = get_invoice_status("CUST-999")
    assert res["customer_id"] == "CUST-999"
    assert res["status"] == "Paid"

def test_run_network_diagnostic():
    res = run_network_diagnostic("ROUTER-1")
    assert res["router_id"] == "ROUTER-1"
    assert res["packet_loss_pct"] == 15.0

def test_open_support_ticket():
    res = open_support_ticket("CUST-999", "Blinking red light")
    assert res["customer_id"] == "CUST-999"
    assert "TICK-" in res["ticket_id"]

def test_available_tools_registry():
    assert len(AVAILABLE_TOOLS) == 3
