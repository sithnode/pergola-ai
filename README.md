# Pergola Paradise — AI-Powered Dropshipping Store

A full-stack dropshipping business for pergolas, powered by Claude AI customer service. Customers browse a product catalog, chat with an AI sales advisor, get instant quotes, and place orders — all without human intervention.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent | Claude claude-sonnet-4-6 (Anthropic) with native tool use |
| Backend | FastAPI (Python 3.11) |
| Storefront | Static HTML + Tailwind CSS |
| Automation | n8n (order notifications, daily inventory sync) |
| Containers | Docker Compose |

## Project Structure

```
pergola-ai/
├── agent/               # AI customer service backend (FastAPI)
│   ├── main.py          # /chat endpoint, tool loop
│   ├── prompts.py       # Claude system prompt
│   ├── tools.py         # Tool implementations + Anthropic schemas
│   └── requirements.txt
├── catalog/
│   ├── products.json    # Master product catalog (source of truth)
│   └── sync.py          # Supplier API sync script
├── orders/
│   ├── order_handler.py # Order CRUD
│   └── notifications.py # Email/SMS notifications
├── storefront/
│   ├── index.html       # Landing page + product grid
│   ├── products.json    # Static copy of catalog for the frontend
│   └── chat-widget.js   # Floating AI chat bubble
├── n8n/workflows/
│   ├── new_order.json        # Fires when AI creates an order
│   ├── order_fulfilled.json  # Fires when supplier ships
│   └── daily_sync.json       # 6 AM inventory + pricing sync
├── docs/
│   ├── architecture.md       # System design
│   ├── supplier-setup.md     # Connect dropship suppliers
│   └── agent-customization.md # Tune the AI persona and tools
├── docker-compose.yml
└── .env.example
```

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/waltergalani/pergola-ai
cd pergola-ai
cp .env.example .env
```

Edit `.env` and set your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Storefront | http://localhost:8080 |
| Agent API | http://localhost:8000 |
| n8n Automation | http://localhost:5678 (admin/changeme) |

### 3. Test the chat agent directly

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What pergolas do you have under $2000?"}'
```

### 4. Run the agent locally (no Docker)

```bash
cd agent
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open `storefront/index.html` in your browser (or serve it with `python -m http.server 8080` from the `storefront/` directory).

## How the AI Agent Works

The agent uses Claude's native tool use to act on real data:

1. **Customer sends a message** → chat widget POSTs to `/chat`
2. **Claude decides what to do** — may call one or more tools:
   - `check_inventory(sku)` → reads `catalog/products.json`
   - `generate_quote(sku, quantity)` → calculates price + shipping + tax
   - `create_order(...)` → writes to `orders/orders.json`
   - `get_order_status(order_id)` → reads order history
3. **Tool results feed back into Claude** → it writes the final reply
4. **New orders trigger n8n** → customer gets email, supplier gets the order

## Connecting Suppliers

See [docs/supplier-setup.md](docs/supplier-setup.md) for step-by-step instructions on connecting dropship supplier APIs.

## Customizing the AI Agent

See [docs/agent-customization.md](docs/agent-customization.md) to change the agent's name, personality, product knowledge, or add new tools.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system diagram and data flow.

## Environment Variables

See `.env.example` for all required and optional configuration.

## License

MIT
