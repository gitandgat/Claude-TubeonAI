"""Tiny local write-back API for the Job-agent dashboard's Notes editor.

Stdlib-only (http.server), bound to 127.0.0.1 only — never exposed beyond
this machine. The only thing it can do is patch the "notes" field of a
single application entry in applications.json, using the same load/save
pattern tracker.py already uses so the file format never diverges.

Run alongside `npm run dev` in the Job-agent repo:
    python3 dashboard_api.py

Route:
    PATCH /api/applications/<job_id>/notes   body: {"notes": "..."}
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import tracker

HOST = "127.0.0.1"
PORT = 8321

CORS_HEADERS = {
    "Access-Control-Allow-Origin": f"http://{HOST}:5173",
    "Access-Control-Allow-Methods": "PATCH, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_PATCH(self) -> None:
        parts = urlparse(self.path).path.strip("/").split("/")
        # expected: ["api", "applications", "<job_id>", "notes"]
        if len(parts) != 4 or parts[0:2] != ["api", "applications"] or parts[3] != "notes":
            self._send_json(404, {"error": "Not found"})
            return

        job_id = parts[2]
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        notes = payload.get("notes")
        if not isinstance(notes, str):
            self._send_json(400, {"error": "'notes' must be a string"})
            return

        data = tracker._load()
        if job_id not in data:
            self._send_json(404, {"error": f"No application with id '{job_id}'"})
            return

        data[job_id]["notes"] = notes
        tracker._save(data)
        self._send_json(200, {"ok": True, "id": job_id, "notes": notes})

    def log_message(self, format: str, *args) -> None:
        print(f"[dashboard_api] {self.address_string()} - {format % args}")


def main() -> None:
    server = HTTPServer((HOST, PORT), Handler)
    print(f"[dashboard_api] Listening on http://{HOST}:{PORT} (notes write-back only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
