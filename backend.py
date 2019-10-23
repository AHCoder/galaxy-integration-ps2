import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import os

import config
import website


class BackendClient:
    def __init__(self, plugin):
        self.auth_server = AuthenticationServer()
        self.plugin = plugin


class AuthenticationHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if "setpath" in self.path:
            self._set_headers()
            parse_result = urlparse(self.path)
            params = parse_qs(parse_result.query)
            self.plugin.config.cfg["Paths"]["roms_path"] = params["romspath"][0]
            self.plugin.config.cfg["Method"]["method"] = params["method"][0]
            self.plugin.config.cfg["Method"]["api_key"] = params["apikey"][0]
            with open(os.path.expandvars(config.CONFIG_LOC), "w", encoding="utf-8") as configfile:
                self.plugin.config.cfg.write(configfile)
            self.wfile.write("<script>window.location=\"/end\";</script>".encode("utf8"))
            return

        self._set_headers()
        self.wfile.write(dummy.dummy.website.encode("utf8"))


class AuthenticationServer(threading.Thread):
    def __init__(self, port = 80):
        super().__init__()
        self.path = ""
        server_address = ('localhost', port)
        self.httpd = HTTPServer(server_address, AuthenticationHandler)
        self.port = self.httpd.server_port

    def run(self):
        self.httpd.serve_forever()
