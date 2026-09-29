"""Append-only audit log. JSON lines for the hackathon; this becomes the
antz_ai_interactions table (and your evaluation dataset) later."""
import json
import os
from datetime import datetime, timezone

from .config import settings


def log_interaction(**fields) -> None:
    os.makedirs(os.path.dirname(settings.audit_log_path) or ".", exist_ok=True)
    record = {"ts": datetime.now(timezone.utc).isoformat(), **fields}
    with open(settings.audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
