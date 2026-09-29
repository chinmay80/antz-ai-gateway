import json
import time
import uuid

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from .audit import log_interaction
from .auth import get_user_context
from .config import settings
from .llm import LLMError, stream_chat
from .prompts import system_prompt
from .schemas import ChatRequest, UserContext

app = FastAPI(title="Antz AI Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


def sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.mistral_model, "mock": settings.mock_llm}


@app.get("/")
async def test_page():
    return FileResponse("static/chat.html")


@app.post("/chat")
async def chat(req: ChatRequest, user: UserContext = Depends(get_user_context)):
    request_id = str(uuid.uuid4())
    messages = [{"role": "system", "content": system_prompt(user, req.screen)}]
    messages += [m.model_dump() for m in req.messages]

    async def events():
        started = time.monotonic()
        parts: list[str] = []
        error = None
        yield sse({"type": "start", "request_id": request_id})
        try:
            async for delta in stream_chat(messages):
                parts.append(delta)
                yield sse({"type": "delta", "text": delta})
        except LLMError as e:
            error = str(e)
            yield sse({"type": "error", "message": "The assistant is unavailable right now. You can keep using Antz normally."})
        finally:
            log_interaction(
                request_id=request_id,
                kind="chat",
                user_id=user.user_id,
                zoo_id=user.zoo_id,
                screen=req.screen,
                platform=req.platform,
                prompt=req.messages[-1].content,
                output="".join(parts),
                error=error,
                latency_ms=int((time.monotonic() - started) * 1000),
                model=settings.mistral_model,
            )
        yield sse({"type": "done"})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
