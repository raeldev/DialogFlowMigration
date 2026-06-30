import time
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("gecx.simulator")

class DialogflowSimulator:
    """
    Simulates a legacy Dialogflow ES/CX rigid rule-based chatbot state machine.
    Demonstrates limitations of intent matching vs GenAI agents:
    - Fails on compound questions or out-of-domain variations
    - Requires exact keyword / regex intent matching
    - Lacks dynamic RAG grounding
    """
    def __init__(self):
        self.intents = {
            "billing.invoice": ["invoice", "bill", "charge"],
            "support.router": ["router", "wifi", "internet", "blinking"]
        }

    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        msg_lower = user_message.lower()
        
        matched_intent = None
        for intent_name, keywords in self.intents.items():
            if any(kw in msg_lower for kw in keywords):
                matched_intent = intent_name
                break
                
        if matched_intent == "billing.invoice":
            reply = "To check your invoice, please log in to the portal at apex.example.com/billing."
            success = True
        elif matched_intent == "support.router":
            reply = "Please restart your router by unplugging it for 30 seconds."
            success = True
        else:
            reply = "I didn't understand that. Please choose from: Billing or Technical Support."
            success = False
            
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        logger.info(json.dumps({
            "event": "dialogflow_legacy_turn",
            "session_id": session_id,
            "matched_intent": matched_intent,
            "success": success,
            "latency_ms": round(latency_ms, 2)
        }))
        
        return {
            "session_id": session_id,
            "reply": reply,
            "matched_intent": matched_intent or "Default Fallback Intent",
            "success": success,
            "latency_ms": round(latency_ms, 2)
        }
