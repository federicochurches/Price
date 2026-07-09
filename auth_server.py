"""HTTP service that serves the staging site and validates AD credentials."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ad_auth_service import AuthenticationConfig, authenticate_ad_user


_SAFE_ERROR_CODES = {
    "missing_credentials",
    "authentication_not_configured",
    "invalid_credentials",
    "ldap3_not_installed",
}


def is_within_root(target: Path, root: Path) -> bool:
    """True if ``target`` is ``root`` or a descendant of it.

    Comparing resolved Path objects (not strings) avoids the classic
    startswith() bug where a sibling directory whose name extends the
    root's name (e.g. root=".../Price", target=".../Price_stage/x")
    would incorrectly pass a naive string-prefix check.
    """
    target = target.resolve()
    root = root.resolve()
    return target == root or root in target.parents


class AuthHandler(BaseHTTPRequestHandler):
    root_dir = Path(os.getcwd())

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/auth/validate':
            self._send_json({'ok': False, 'error': 'method_not_allowed'})
            return
        self._serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/auth/validate':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8')
        try:
            payload = json.loads(body or '{}')
        except json.JSONDecodeError:
            payload = {}

        username = str(payload.get('username', '')).strip()
        password = str(payload.get('password', ''))
        config = AuthenticationConfig.from_environment()
        result = authenticate_ad_user(username, password, config)
        # No exponer detalle de servidor/puerto/excepción a un caller anónimo de
        # la red — solo códigos de error conocidos salen tal cual; el resto se
        # loguea server-side y se devuelve genérico.
        if not result.get('ok') and result.get('error') not in _SAFE_ERROR_CODES:
            print(f"[auth] error interno de autenticación: {result.get('error')}")
            result = {**result, 'error': 'auth_service_unavailable'}
        self._send_json(result)

    def _serve_static(self, path: str) -> None:
        rel_path = path.split('?', 1)[0].split('#', 1)[0]
        rel_path = rel_path.lstrip('/') or 'index.html'
        target = self.root_dir / rel_path
        if not is_within_root(target, self.root_dir):
            self.send_error(403)
            return
        target = target.resolve()
        if target.is_dir():
            target = target / 'index.html'
        if not target.exists():
            self.send_error(404)
            return
        content_type = 'text/html; charset=utf-8' if target.suffix.lower() == '.html' else 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(target.read_bytes())

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_server(host: str = '0.0.0.0', port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), AuthHandler)
    print(f'Auth server listening on {host}:{port}')
    server.serve_forever()


if __name__ == '__main__':
    run_server()
