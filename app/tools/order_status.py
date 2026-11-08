import json
from pathlib import Path


class OrderStatusTool:

    def __init__(self):
        self.orders_path = Path("data/orders/orders.json")

    def check_order_status(self, order_id: str, customer_id: str) -> dict:

        if not self.orders_path.exists():
            return {
                "success": False,
                "message": "Order database unavailable.",
                "escalation_score": 1.0,
                "requires_human": True
            }

        try:
            orders = json.loads(
                self.orders_path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            return {
                "success": False,
                "message": "Unable to read order database.",
                "escalation_score": 1.0,
                "requires_human": True
            }

        for order in orders:

            if order["order_id"] == order_id:

                if order["customer_id"] != customer_id:
                    return {
                        "success": False,
                        "message": "Order verification failed.",
                        "escalation_score": 1.0,
                        "requires_human": True
                    }

                status = order["status"]

                escalation_scores = {
                    "placed": 0.1,
                    "confirmed": 0.1,
                    "packed": 0.2,
                    "shipped": 0.2,
                    "out_for_delivery": 0.3,
                    "delivered": 0.1,
                    "cancelled": 0.7,
                    "return_requested": 0.8
                }

                score = escalation_scores.get(status, 1.0)

                return {
                    "success": True,
                    "order_id": order_id,
                    "status": status,
                    "estimated_delivery": order["estimated_delivery"],
                    "escalation_score": score,
                    "requires_human": score >= 0.7
                }

        return {
            "success": False,
            "message": "Order not found.",
            "escalation_score": 1.0,
            "requires_human": True
        }
