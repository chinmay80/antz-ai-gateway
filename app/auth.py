"""Resolve who is calling the gateway.

Real path: forward the user's existing Antz/CI4 bearer token to a CI4
"whoami" endpoint. CI4 validates it and returns the user's context, so the
gateway never needs its own copy of auth logic or DB credentials.

Hackathon fallback: if CI4_WHOAMI_URL is empty, every request runs as
DEMO_USER. Say this openly in the demo.
"""
import httpx
from fastapi import Header, HTTPException

from .config import settings
from .schemas import UserContext

DEMO_USER = UserContext(
    user_id=1,
    name="Demo Keeper",
    role="Animal Keeper",
    zoo_id=1,
    zoo_name="Demo Zoo",
    site_ids=[1],
    site_names=["Main Site"],
)


async def get_user_context(authorization: str | None = Header(default=None)) -> UserContext:
    if not settings.ci4_whoami_url:
        return DEMO_USER

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        async with httpx.AsyncClient(timeout=settings.ci4_timeout_seconds) as client:
            resp = await client.get(settings.ci4_whoami_url, headers={"Authorization": authorization})
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Could not reach Antz to verify your session")

    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Session expired. Log in to Antz again.")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Antz returned an unexpected response")

    body = resp.json()
    return UserContext(**body.get("data", body))
