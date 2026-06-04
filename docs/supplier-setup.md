# Supplier Setup

## Connecting a Dropship Supplier

Each supplier needs an API key and base URL. Add them to `.env`:

```bash
SUPPLIER_WOODCRAFT_API_KEY=sk-xxx
SUPPLIER_WOODCRAFT_API_URL=https://api.woodcraftoutdoors.com/v1
```

Then implement the supplier-specific sync logic in `catalog/sync.py` inside `sync_supplier()`.

## Typical Supplier API Shapes

Most supplier APIs follow one of these patterns:

### REST (most common)
```
GET /products          → [{sku, name, price, inventory, ...}]
POST /orders           → {order_id, ...}
GET /orders/{id}       → {status, tracking_number, carrier}
```

### EDI / FTP
Some legacy suppliers deliver inventory files via SFTP. Use n8n's SFTP node to download and parse.

## Adding a New Supplier

1. Get API credentials from the supplier
2. Add env vars to `.env` and `.env.example`
3. Add supplier config to the `suppliers` list in `catalog/sync.py`
4. Implement the `sync_supplier()` fetch for that supplier's API shape
5. Map their SKUs to your catalog's `supplier_sku` field in `catalog/products.json`
6. Add the product(s) to `catalog/products.json` with `supplier` and `supplier_sku` set
7. Copy `catalog/products.json` to `storefront/products.json` (or automate in the sync script)

## Order Forwarding

When the AI agent creates an order via the `create_order` tool:

1. The order is saved to `orders/orders.json`
2. The n8n `new_order` workflow fires (via webhook)
3. n8n forwards the order to your supplier's order API

Update the **Forward to Supplier** node in `n8n/workflows/new_order.json` with your supplier's endpoint and auth header.

## Tracking Updates

Configure your supplier to POST tracking updates to:
```
POST http://your-n8n-host:5678/webhook/order-fulfilled
{
  "order_id": "PG-20260604-A1B2C3",
  "customer_email": "...",
  "tracking_number": "...",
  "carrier": "FedEx"
}
```

The `order_fulfilled` n8n workflow will update the order status and email the customer.
