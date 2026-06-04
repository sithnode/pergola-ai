#!/usr/bin/env python3
"""
Sync product catalog from supplier APIs.
Run daily via the n8n daily_sync workflow or directly: python sync.py
"""
import json
import os
from datetime import datetime
from pathlib import Path

import httpx

CATALOG_FILE = Path(__file__).parent / "products.json"


def sync_supplier(name: str, api_key: str, api_url: str) -> list[dict]:
    """
    Fetch inventory and pricing updates from a supplier API.
    Returns list of {supplier_sku, inventory, price} dicts.
    """
    if not api_key or not api_url:
        print(f"[Sync] Skipping {name} — API key or URL not configured")
        return []

    # Each supplier has a different API shape — implement per-supplier below.
    # Example shape assumed: GET /products → [{sku, inventory, price}]
    try:
        resp = httpx.get(
            f"{api_url}/products",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[Sync] {name} failed: {e}")
        return []


def run_sync():
    catalog = json.loads(CATALOG_FILE.read_text())

    suppliers = [
        {
            "name": "WoodCraft Outdoors",
            "api_key": os.getenv("SUPPLIER_WOODCRAFT_API_KEY", ""),
            "api_url": os.getenv("SUPPLIER_WOODCRAFT_API_URL", ""),
        },
        {
            "name": "MetalWorks Pro",
            "api_key": os.getenv("SUPPLIER_METALWORKS_API_KEY", ""),
            "api_url": os.getenv("SUPPLIER_METALWORKS_API_URL", ""),
        },
        {
            "name": "VinylOutdoor Supply",
            "api_key": os.getenv("SUPPLIER_VINYLOUTDOOR_API_KEY", ""),
            "api_url": os.getenv("SUPPLIER_VINYLOUTDOOR_API_URL", ""),
        },
    ]

    updated = 0
    for supplier in suppliers:
        updates = sync_supplier(supplier["name"], supplier["api_key"], supplier["api_url"])
        for update in updates:
            for product in catalog["products"]:
                if product["supplier_sku"] == update.get("sku"):
                    if "inventory" in update:
                        product["inventory"] = update["inventory"]
                    if "price" in update:
                        product["price"] = update["price"]
                    updated += 1

    catalog["last_updated"] = datetime.now().isoformat()
    CATALOG_FILE.write_text(json.dumps(catalog, indent=2))
    print(f"[Sync] Complete — {updated} product(s) updated at {catalog['last_updated']}")


if __name__ == "__main__":
    run_sync()
