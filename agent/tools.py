import json
import uuid
import os
from datetime import datetime
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "catalog" / "products.json"
ORDERS_PATH = Path(__file__).parent.parent / "orders" / "orders.json"


def _load_catalog() -> dict:
    with open(CATALOG_PATH) as f:
        return json.load(f)


def _load_orders() -> list:
    if not ORDERS_PATH.exists():
        return []
    with open(ORDERS_PATH) as f:
        return json.load(f)


def _save_orders(orders: list):
    ORDERS_PATH.parent.mkdir(exist_ok=True)
    with open(ORDERS_PATH, "w") as f:
        json.dump(orders, f, indent=2)


# ── Tool implementations ───────────────────────────────────────────────────────

def check_inventory(sku: str, quantity: int = 1) -> dict:
    catalog = _load_catalog()
    product = next((p for p in catalog["products"] if p["sku"] == sku), None)
    if not product:
        return {"available": False, "message": f"Product with SKU '{sku}' not found in catalog."}

    in_stock = product.get("inventory", 0) >= quantity
    return {
        "sku": sku,
        "name": product["name"],
        "available": in_stock,
        "quantity_in_stock": product.get("inventory", 0),
        "price": product["price"],
        "sale_price": product.get("sale_price"),
        "lead_time_days": product.get("lead_time_days", 7),
        "material": product["material"],
        "dimensions": product["dimensions"],
    }


def generate_quote(sku: str, quantity: int = 1, zip_code: str = None) -> dict:
    catalog = _load_catalog()
    product = next((p for p in catalog["products"] if p["sku"] == sku), None)
    if not product:
        return {"error": f"Product with SKU '{sku}' not found."}

    unit_price = product.get("sale_price") or product["price"]
    subtotal = round(unit_price * quantity, 2)
    # Freight shipping estimate: free over $1500, otherwise ~8% of subtotal
    shipping = 0.0 if subtotal >= 1500 else round(subtotal * 0.08, 2)
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + shipping + tax, 2)

    return {
        "sku": sku,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": subtotal,
        "estimated_shipping": shipping,
        "shipping_note": "Free freight shipping (order over $1,500)" if shipping == 0 else "Freight carrier — actual rate confirmed at checkout",
        "estimated_tax": tax,
        "total": total,
        "currency": "USD",
        "quote_valid_days": 7,
        "lead_time_days": product.get("lead_time_days", 7),
    }


def create_order(
    customer_name: str,
    customer_email: str,
    sku: str,
    quantity: int,
    shipping_address: str,
) -> dict:
    catalog = _load_catalog()
    product = next((p for p in catalog["products"] if p["sku"] == sku), None)
    if not product:
        return {"error": f"Product with SKU '{sku}' not found."}

    unit_price = product.get("sale_price") or product["price"]
    order_id = f"PG-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    order = {
        "order_id": order_id,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "customer": {"name": customer_name, "email": customer_email},
        "items": [
            {
                "sku": sku,
                "name": product["name"],
                "quantity": quantity,
                "unit_price": unit_price,
                "total": round(unit_price * quantity, 2),
            }
        ],
        "shipping_address": shipping_address,
        "total": round(unit_price * quantity, 2),
        "supplier": product["supplier"],
        "supplier_sku": product["supplier_sku"],
    }

    orders = _load_orders()
    orders.append(order)
    _save_orders(orders)

    return {
        "success": True,
        "order_id": order_id,
        "message": f"Order {order_id} created successfully. A confirmation will be sent to {customer_email}.",
        "estimated_delivery_days": product.get("lead_time_days", 7) + 3,
        "total": order["total"],
    }


def get_order_status(order_id: str) -> dict:
    orders = _load_orders()
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return {"error": f"Order '{order_id}' not found. Please check the order ID and try again."}

    return {
        "order_id": order["order_id"],
        "status": order["status"],
        "created_at": order["created_at"],
        "items": order["items"],
        "total": order["total"],
        "customer_email": order["customer"]["email"],
        "shipping_address": order.get("shipping_address"),
        "tracking_number": order.get("tracking_number"),
        "carrier": order.get("carrier"),
    }


# ── Anthropic tool schemas ─────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "check_inventory",
        "description": "Check availability and current pricing for a pergola product by its SKU. Use before quoting or ordering to confirm the item is in stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Product SKU (e.g., PG-CLW-1012). Ask the customer or browse the catalog to find it.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units the customer wants (default: 1).",
                    "default": 1,
                },
            },
            "required": ["sku"],
        },
    },
    {
        "name": "generate_quote",
        "description": "Generate a detailed price quote including shipping and tax estimates. Always show the customer a quote before asking them to commit to an order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "Product SKU"},
                "quantity": {"type": "integer", "description": "Number of units", "default": 1},
                "zip_code": {
                    "type": "string",
                    "description": "Customer ZIP code for shipping estimate (optional)",
                },
            },
            "required": ["sku"],
        },
    },
    {
        "name": "create_order",
        "description": "Place a new order for a customer. ONLY call this after the customer has explicitly confirmed they want to place the order and you have collected all required information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Full name of the customer"},
                "customer_email": {"type": "string", "description": "Customer email address for confirmation"},
                "sku": {"type": "string", "description": "Product SKU to order"},
                "quantity": {"type": "integer", "description": "Number of units to order"},
                "shipping_address": {
                    "type": "string",
                    "description": "Full shipping address including street, city, state, and ZIP",
                },
            },
            "required": ["customer_name", "customer_email", "sku", "quantity", "shipping_address"],
        },
    },
    {
        "name": "get_order_status",
        "description": "Look up the current status of an existing order using its order ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID in format PG-YYYYMMDD-XXXXXX (e.g., PG-20260604-A1B2C3)",
                }
            },
            "required": ["order_id"],
        },
    },
]


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> dict:
    dispatch = {
        "check_inventory": check_inventory,
        "generate_quote": generate_quote,
        "create_order": create_order,
        "get_order_status": get_order_status,
    }
    fn = dispatch.get(name)
    if not fn:
        return {"error": f"Unknown tool: {name}"}
    try:
        return fn(**inputs)
    except Exception as e:
        return {"error": f"Tool '{name}' failed: {str(e)}"}
