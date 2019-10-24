import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import config


class AuthenticationHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if "setconfig" in self.path:
            self._set_headers()
            parse_result = urlparse(self.path)
            params = parse_qs(parse_result.query)
            logging.debug("Params are %s", params)
            config_parse = config.Config()
            config_parse.cfg["Paths"]["roms_path"] = params["romspath"][0]
            config_parse.cfg["Paths"]["emu_path"] = params["emupath"][0]
            config_parse.cfg["Paths"]["config_path"] = params["configpath"][0]
            config_parse.cfg["Method"]["method"] = params["method"][0]
            config_parse.cfg["Method"]["api_key"] = params["apikey"][0]
            config_parse.cfg["EmuSettings"]["emu_fullscreen"] = True if "fullscreen" in params else False
            config_parse.cfg["EmuSettings"]["emu_no_gui"] = True if "nogui" in params else False
            config_parse.cfg["EmuSettings"]["emu_config"] = True if "config" in params else False
            with open(os.path.expandvars(config.CONFIG_LOC), "w", encoding="utf-8") as configfile:
                config_parse.cfg.write(configfile)
            logging.debug("Config has been written as %s", configfile)
            self.wfile.write("<script>window.location=\"/end\";</script>".encode("utf8"))
            return

        self._set_headers()
        file_loc = os.path.join(os.path.dirname(__file__), "website\index.html")
        logging.debug("HTML file is located in %s", file_loc)
        with open(file_loc, "rb") as website:
            self.wfile.write(website.read())


class AuthenticationServer(threading.Thread):
    def __init__(self, port = 8080):
        super().__init__()
        self.path = ""
        server_address = ('localhost', port)
        self.httpd = HTTPServer(server_address, AuthenticationHandler)
        self.port = self.httpd.server_port

    def run(self):
        self.httpd.serve_forever()
