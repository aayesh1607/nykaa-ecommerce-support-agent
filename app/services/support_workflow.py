import re
from functools import lru_cache

from app.rag.policy_rag import PolicyRAG
from app.tools.order_status import OrderStatusTool


@lru_cache(maxsize=1)
def get_rag():
    rag = PolicyRAG()
    rag.build_index()
    return rag


class CustomerSupportWorkflow:

    def __init__(self):
        self.orders = OrderStatusTool()

    def process(self, question: str, order_id: str = "", customer_id: str = "") -> dict:
        question = question.strip()

        if not question:
            return self._response(
                "Please enter a customer support question.",
                "validation",
                True,
                1.0,
                []
            )

        if len(question) > 2000:
            return self._response(
                "Your message is too long. Please contact human support.",
                "security",
                True,
                1.0,
                []
            )

        suspicious_patterns = [
            r"ignore (all |previous |your )?instructions",
            r"reveal (your |the )?(system|secret|password|api key)",
            r"bypass (the )?(security|policy|rules)",
            r"show (me )?(all |other )?customers",
        ]

        if any(re.search(p, question, re.I) for p in suspicious_patterns):
            return self._response(
                "This request cannot be processed automatically.",
                "security",
                True,
                1.0,
                []
            )

        lower = question.lower()

        order_keywords = [
            "order status", "track", "tracking",
            "where is my order", "delivery status"
        ]

        if order_id or any(word in lower for word in order_keywords):
            if not order_id or not customer_id:
                return self._response(
                    "Please provide your order ID and customer ID to check your order.",
                    "order",
                    False,
                    0.2,
                    []
                )

            result = self.orders.check_order_status(order_id, customer_id)

            if not result["success"]:
                return self._response(
                    result["message"],
                    "order",
                    result["requires_human"],
                    result["escalation_score"],
                    []
                )

            return self._response(
                f"Order {order_id} is currently {result['status']}. "
                f"Estimated delivery: {result['estimated_delivery']}.",
                "order",
                result["requires_human"],
                result["escalation_score"],
                []
            )

        rag = get_rag()
        results = rag.search(question, strategy="full", limit=1)

        if not results:
            return self._response(
                "I could not find a relevant policy. Human support is required.",
                "policy",
                True,
                0.9,
                []
            )

        match = results[0]

        # Chroma's default distance is not a calibrated confidence score.
        # This conservative threshold is provisional and needs evaluation.
        if match["distance"] > 1.1:
            return self._response(
                "I could not confidently match your question to a policy. "
                "Please contact human support.",
                "policy",
                True,
                0.8,
                []
            )

        policy_text = match["text"].split("\n\n", 1)[-1]

        return self._response(
            policy_text,
            "policy",
            False,
            0.1,
            [match["source"]]
        )

    @staticmethod
    def _response(answer, category, requires_human, escalation_score, sources):
        return {
            "answer": answer,
            "category": category,
            "requires_human": requires_human,
            "escalation_score": escalation_score,
            "sources": sources,
            "mode": "MOCK_LLM"
        }
