import json
import os
from typing import Optional

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prompts import SYSTEM_PROMPT
from tools import TOOLS, execute_tool

load_dotenv()

app = FastAPI(title="Pergola Paradise AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    conversation_history: list = []


class ChatResponse(BaseModel):
    response: str
    conversation_history: list
    session_id: Optional[str] = None


def _serialize_content(content) -> list:
    """Convert Anthropic content blocks to JSON-serializable dicts for history storage."""
    result = []
    for block in content:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append(
                {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
            )
    return result


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    messages = list(request.conversation_history)
    messages.append({"role": "user", "content": request.message})
    current_messages = list(messages)
    response = None

    for _ in range(10):  # Guard against infinite tool-call loops
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=current_messages,
        )

        if response.stop_reason != "tool_use":
            break

        serialized = _serialize_content(response.content)
        current_messages.append({"role": "assistant", "content": serialized})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        current_messages.append({"role": "user", "content": tool_results})

    if response is None:
        raise HTTPException(status_code=500, detail="No response from model")

    text_response = " ".join(
        block.text for block in response.content if block.type == "text"
    )
    current_messages.append(
        {"role": "assistant", "content": _serialize_content(response.content)}
    )

    return ChatResponse(
        response=text_response,
        conversation_history=current_messages,
        session_id=request.session_id,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL}


@app.get("/products")
async def get_products():
    catalog_path = os.path.join(os.path.dirname(__file__), "..", "catalog", "products.json")
    with open(catalog_path) as f:
        return json.load(f)
