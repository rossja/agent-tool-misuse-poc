import json
import queue
import threading
from typing import Any, Union

from flask import Flask, Response, render_template, request, stream_with_context
from langchain.callbacks.base import BaseCallbackHandler

from agent import convert_history, create_agent

app = Flask(__name__)


class StreamingCallbackHandler(BaseCallbackHandler):
    """Forwards agent reasoning events to a queue consumed by an SSE stream."""

    def __init__(self, q: queue.Queue):
        self.q = q

    def _put(self, event: dict) -> None:
        self.q.put(event)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._put({"type": "token", "content": token})

    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        self._put({
            "type": "agent_action",
            "tool": action.tool,
            "input": str(action.tool_input),
        })

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: Any) -> None:
        self._put({
            "type": "tool_start",
            "tool": serialized.get("name", "unknown"),
            "input": input_str,
        })

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        self._put({"type": "tool_end", "output": str(output)})

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        self._put({"type": "tool_error", "error": str(error)})

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        self._put({
            "type": "agent_finish",
            "output": finish.return_values.get("output", ""),
        })
        self.q.put(None)  # sentinel — signals stream end


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return {"error": "empty message"}, 400

    q: queue.Queue = queue.Queue()
    streaming_handler = StreamingCallbackHandler(q)

    def run_agent():
        try:
            agent = create_agent(extra_callbacks=[streaming_handler])
            agent.invoke({
                "input": user_message,
                "chat_history": convert_history(history),
            })
        except Exception as e:
            q.put({"type": "error", "content": str(e)})
            q.put(None)

    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()

    def generate():
        while True:
            item = q.get()
            if item is None:
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                break
            yield f"data: {json.dumps(item)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
