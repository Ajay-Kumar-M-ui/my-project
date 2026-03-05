#!/usr/bin/env python3
"""Simple backend server with a SQLite database connection."""

import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = os.getenv("DB_PATH", "app.db")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()


class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "database": DB_PATH})
            return

        if self.path == "/users":
            with get_connection() as conn:
                rows = conn.execute("SELECT id, name, email FROM users ORDER BY id").fetchall()
            users = [dict(row) for row in rows]
            self._send_json(200, {"users": users})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/users":
            self._send_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            name = payload["name"].strip()
            email = payload["email"].strip()
            if not name or not email:
                raise ValueError("name and email are required")
        except (json.JSONDecodeError, KeyError, ValueError):
            self._send_json(400, {"error": "Provide valid JSON with non-empty name and email"})
            return

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (name, email),
                )
                conn.commit()
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            self._send_json(409, {"error": "Email already exists"})
            return

        self._send_json(201, {"id": user_id, "name": name, "email": email})


def run() -> None:
    initialize_db()
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"Server running on http://{HOST}:{PORT} using database '{DB_PATH}'")
    server.serve_forever()


if __name__ == "__main__":
    run()
