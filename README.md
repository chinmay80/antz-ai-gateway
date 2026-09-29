# Antz AI Gateway (Day 1)

FastAPI service that sits between the Antz apps and the model.
Day 1 delivers: health check, streaming `/chat`, a test chat page, user
context from CI4 (or a demo user), and an audit log.

## Run

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # add MISTRAL_API_KEY, or set MOCK_LLM=true
    uvicorn app.main:app --reload --port 8000

Open http://localhost:8000 for the test chat page.

## Check it works

    curl localhost:8000/health
    curl -N -X POST localhost:8000/chat -H 'Content-Type: application/json' \
      -d '{"messages":[{"role":"user","content":"How do I report an incident?"}]}'

## Layout

    app/main.py      routes: /health, /chat (SSE), / (test page)
    app/llm.py       Mistral streaming client (swap base URL for vLLM later)
    app/auth.py      user context from CI4 whoami, or DEMO_USER
    app/prompts.py   system prompt with user/zoo/screen context
    app/audit.py     JSON-lines audit log -> DB table later
    ci4/AiGateway.php  CI4 whoami endpoint sketch

## SSE event format

    data: {"type":"start","request_id":"..."}
    data: {"type":"delta","text":"..."}
    data: {"type":"error","message":"..."}
    data: {"type":"done"}
