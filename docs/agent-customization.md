# Agent Customization

## Changing the AI's Personality

Edit `agent/prompts.py`. The `SYSTEM_PROMPT` string controls everything about how the agent behaves — its name, tone, knowledge, and rules.

Key sections to tune:

| Section | What to change |
|---------|----------------|
| "You are Alex…" | Agent name and company name |
| "## Your Role" | High-level mission |
| "## Product Knowledge" | Materials, sizes, warranties |
| "## Sales Approach" | How aggressively it pushes for a sale |
| "## Rules" | Hard constraints (never do X) |

### Example: Making the agent more casual
```python
SYSTEM_PROMPT = """You are Sam, a chill outdoor enthusiast at Backyard Vibes Co.
Use casual language — contractions, conversational tone, maybe the occasional emoji.
...
"""
```

## Adding New Tools

Tools live in `agent/tools.py`. To add a tool:

1. Write the Python function:
```python
def check_lead_time(sku: str, zip_code: str) -> dict:
    # Your logic here
    return {"sku": sku, "estimated_days": 10}
```

2. Add the Anthropic schema to the `TOOLS` list:
```python
{
    "name": "check_lead_time",
    "description": "Get an estimated delivery lead time for a product based on ZIP code",
    "input_schema": {
        "type": "object",
        "properties": {
            "sku": {"type": "string"},
            "zip_code": {"type": "string"}
        },
        "required": ["sku", "zip_code"]
    }
}
```

3. Add it to the dispatcher in `execute_tool()`:
```python
dispatch = {
    ...
    "check_lead_time": check_lead_time,
}
```

4. Mention the new tool in the system prompt so Claude knows when to use it.

## Adjusting the Model

The model is set in `agent/main.py`:
```python
MODEL = "claude-sonnet-4-6"
```

Available options (as of 2026):
- `claude-sonnet-4-6` — best balance of quality and speed (recommended)
- `claude-opus-4-8` — highest quality, slower
- `claude-haiku-4-5-20251001` — fastest and cheapest, less capable

## Tuning Response Quality

In `agent/main.py`, adjust the `client.messages.create()` call:

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,      # Increase for longer, more detailed responses
    system=SYSTEM_PROMPT,
    tools=TOOLS,
    messages=current_messages,
)
```

## Extending the Product Catalog

Edit `catalog/products.json`. Each product needs:
- `sku` — unique identifier (used by all tools)
- `supplier_sku` — supplier's part number (used for order forwarding)
- `price`, `inventory`, `lead_time_days` — kept fresh by the daily sync

After editing, copy to `storefront/products.json` so the website reflects the change.
