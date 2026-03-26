import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

LOG_PATH = os.environ.get("AUDIT_LOG_PATH", "/var/log/agent/audit.log")

logging.basicConfig(level=logging.INFO, format="[agent] %(message)s")
logger = logging.getLogger("audit")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def _write(event: dict) -> None:
    entry = json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **event})
    print(f"[AUDIT] {entry}", flush=True)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(entry + "\n")
    except Exception:
        pass


class AuditLogCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized: dict, prompts: list, **kwargs: Any) -> None:
        _write({"event": "llm_start", "prompts": prompts})

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        text = ""
        if response.generations and response.generations[0]:
            text = getattr(response.generations[0][0], "text", "")
        _write({"event": "llm_end", "text": text})

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        _write({"event": "llm_error", "error": str(error)})

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
        tool_name = serialized.get("name", "unknown")
        _write({"event": "tool_start", "tool": tool_name, "input": input_str})

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        _write({"event": "tool_end", "output": str(output)})

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        _write({"event": "tool_error", "error": str(error)})

    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        _write({
            "event": "agent_action",
            "tool": action.tool,
            "tool_input": str(action.tool_input),
        })

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        _write({"event": "agent_finish", "output": finish.return_values.get("output", "")})
