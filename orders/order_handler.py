import json
import uuid
from datetime import datetime
from pathlib import Path

ORDERS_FILE = Path(__file__).parent / "orders.json"


def load_orders() -> list:
    if not ORDERS_FILE.exists():
        return []
    with open(ORDERS_FILE) as f:
        return json.load(f)


def save_orders(orders: list):
    ORDERS_FILE.parent.mkdir(exist_ok=True)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)


def get_order(order_id: str) -> dict | None:
    return next((o for o in load_orders() if o["order_id"] == order_id), None)


def update_order_status(order_id: str, status: str, **extra_fields) -> dict:
    orders = load_orders()
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = status
            order["updated_at"] = datetime.now().isoformat()
            order.update(extra_fields)
            save_orders(orders)
            return order
    raise ValueError(f"Order {order_id} not found")


def fulfill_order(order_id: str, tracking_number: str, carrier: str) -> dict:
    """Mark an order as shipped and record tracking info."""
    return update_order_status(
        order_id,
        status="shipped",
        tracking_number=tracking_number,
        carrier=carrier,
        shipped_at=datetime.now().isoformat(),
    )
