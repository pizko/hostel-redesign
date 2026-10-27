#!/usr/bin/env python3
"""Локальный предпросмотр dist/: /rooms → rooms.html, как на боевом сайте. python3 tools/serve.py [порт]"""
import http.server, os, sys
from functools import partial
DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist")
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = super().translate_path(path)
        if not os.path.exists(p) and os.path.exists(p + ".html"):
            return p + ".html"
        return p
    def log_message(self, *a): pass
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8790
http.server.ThreadingHTTPServer(("127.0.0.1", port), partial(H, directory=DIST)).serve_forever()
