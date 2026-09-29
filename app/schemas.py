from typing import Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=8000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=40)
    screen: str | None = None      # which app screen the user is on
    platform: Literal["web", "mobile"] = "web"


class UserContext(BaseModel):
    user_id: int
    name: str
    role: str
    zoo_id: int
    zoo_name: str
    site_ids: list[int] = []
    site_names: list[str] = []
