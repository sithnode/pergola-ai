# Architecture

## Overview

```
Browser (Storefront)
    │
    │  HTTP POST /chat
    ▼
Agent (FastAPI + Claude claude-sonnet-4-6)
    │
    ├── check_inventory ──► catalog/products.json
    ├── generate_quote  ──► catalog/products.json
    ├── create_order    ──► orders/orders.json
    └── get_order_status ─► orders/orders.json
    │
    │  POST /webhooks/new-order
    ▼
n8n Automation
    ├── Email customer confirmation
    ├── Forward order to supplier API
    └── Daily catalog sync (6 AM cron)
```

## Services

| Service    | Port | Description                                      |
|------------|------|--------------------------------------------------|
| storefront | 8080 | Static HTML/JS served by nginx                   |
| agent      | 8000 | FastAPI app — Claude AI with tool use            |
| n8n        | 5678 | Visual workflow automation (admin: /workflow)     |

## Data Flow

### Chat / Quote Flow
1. Customer types a message in the chat widget
2. `chat-widget.js` POSTs `{message, conversation_history}` to `agent:8000/chat`
3. The agent calls Claude `claude-sonnet-4-6` with the system prompt and tool definitions
4. Claude decides which tools to call (inventory check, quote generation, etc.)
5. The agent executes the tools against `catalog/products.json`
6. Tool results feed back into Claude, which writes the final reply
7. The reply and updated conversation history return to the browser

### Order Flow
1. Customer confirms an order in chat
2. Claude calls `create_order` tool → saved to `orders/orders.json`
3. Agent POSTs to n8n webhook `new-order`
4. n8n emails the customer and forwards the order to the supplier API

### Daily Sync
1. n8n cron fires at 6 AM
2. n8n calls `agent:8000/catalog/sync`
3. Agent calls each configured supplier API and updates `catalog/products.json`
4. n8n emails the admin if any prices or inventory changed

## File Storage

For the starter project, all data is stored in JSON files:
- `catalog/products.json` — master product catalog
- `orders/orders.json` — order records (gitignored — may contain PII)

To scale, replace these with a proper database (Postgres recommended).
See `.env.example` for `DATABASE_URL`.
