from __future__ import annotations

import json
import os
import time
from pathlib import Path


def record(event: str, **fields: object) -> None:
    """Append một sự kiện quan trọng (incident enable/disable, config change) vào audit log riêng."""
    path = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **fields}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
