import os
from http.server import HTTPServer, BaseHTTPRequestHandler


class AttackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/scripts/"):
            script_name = self.path[len("/scripts/"):]
            script_path = os.path.join("scripts", script_name)
            self._serve_file(script_path, "text/plain")
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_file(self, path, content_type):
        if not os.path.exists(path):
            self.send_response(404)
            self.end_headers()
            return
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"[attacker] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9090), AttackerHandler)
    print("[attacker] Listening on :9090", flush=True)
    server.serve_forever()
