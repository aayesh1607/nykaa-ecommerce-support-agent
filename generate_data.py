import json
import random
from pathlib import Path
from datetime import date, timedelta

random.seed(42)

base = Path("data")
orders_dir = base / "orders"
policies_dir = base / "policies"

orders_dir.mkdir(parents=True, exist_ok=True)
policies_dir.mkdir(parents=True, exist_ok=True)

products = [
    "Lakme Foundation",
    "Maybelline Mascara",
    "Nykaa Matte Lipstick",
    "L'Oreal Shampoo",
    "Minimalist Niacinamide Serum",
    "Cetaphil Cleanser",
    "Plum Body Lotion",
    "The Ordinary Hyaluronic Acid",
    "Neutrogena Sunscreen",
    "Mamaearth Face Wash"
]

statuses = [
    "placed",
    "confirmed",
    "packed",
    "shipped",
    "out_for_delivery",
    "delivered",
    "cancelled",
    "return_requested"
]

orders = []

for i in range(1, 51):
    order = {
        "order_id": f"NYK-{i:04d}",
        "customer_id": f"CUST-{i:03d}",
        "product": random.choice(products),
        "quantity": random.randint(1, 3),
        "amount_inr": random.randint(299, 4999),
        "status": random.choice(statuses),
        "order_date": str(date(2026, 10, 1) + timedelta(days=random.randint(0, 30))),
        "estimated_delivery": str(date(2026, 11, 5) + timedelta(days=random.randint(0, 15)))
    }
    orders.append(order)

(orders_dir / "orders.json").write_text(
    json.dumps(orders, indent=2),
    encoding="utf-8"
)

policies = {
    "returns": "Returns may be requested within 7 days of delivery for eligible unused products. Some hygiene-sensitive products are excluded.",
    "refunds": "Approved refunds are processed to the original payment method. Processing time depends on the payment provider.",
    "cancellations": "Orders may be cancelled before dispatch. Once shipped, cancellation may not be available.",
    "shipping": "Shipping availability and charges depend on delivery location, order value, and selected delivery method.",
    "delivery": "Estimated delivery dates are indicative and may change because of logistics delays.",
    "damaged_items": "Customers receiving damaged products should contact support with order details and photographs.",
    "missing_items": "Missing-item claims require order verification and may require package photographs.",
    "payments": "Supported payment methods depend on checkout availability. Customers should never share OTPs or passwords.",
    "cod": "Cash on Delivery availability depends on location, order value, and product eligibility.",
    "exchanges": "Product exchanges depend on category eligibility, stock availability, and inspection.",
    "privacy": "Customer information must only be used for authorized support purposes and should not be exposed to other customers.",
    "escalation": "Complex disputes, suspicious requests, unresolved complaints, and policy exceptions must be escalated to human support."
}

for name, content in policies.items():
    (policies_dir / f"{name}.txt").write_text(
        f"Policy: {name.replace('_', ' ').title()}\n\n{content}\n",
        encoding="utf-8"
    )

print(f"Generated {len(orders)} customer orders.")
print(f"Generated {len(policies)} policy documents.")
print("Nykaa sample dataset created successfully.")
