import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import config


class AuthenticationHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path.endswith(".css"):
            self._set_headers("text/css")
            css_loc = os.path.join(os.path.dirname(__file__), "website\css\main.css")
            with open(css_loc, "rb") as styles:
                self.wfile.write(styles.read())
        if self.path.endswith(".jpg"):
            self._set_headers("image/jpeg")
            image_loc = os.path.join(os.path.dirname(__file__), "website\images\header.jpg")
            with open(image_loc, "rb") as image:
                self.wfile.write(image.read())
        if "setconfig" in self.path:
            self._set_headers("text/html")
            parse_result = urlparse(self.path)
            params = parse_qs(parse_result.query)
            parser = config.Config().cfg
            try:
                parser["Paths"]["roms_path"] = params["romspath"][0]
                parser["Paths"]["emu_path"] = params["emupath"][0] if "emupath" in params else None
                parser["Paths"]["config_path"] = params["configpath"][0] if "configpath" in params else None
                parser["Method"]["method"] = params["method"][0]
                parser["Method"]["api_key"] = params["apikey"][0] if "apikey" in params else None
                parser["EmuSettings"]["emu_fullscreen"] = "True" if "fullscreen" in params else "False"
                parser["EmuSettings"]["emu_no_gui"] = "True" if "nogui" in params else "False"
                parser["EmuSettings"]["emu_config"] = "True" if "config" in params else "False"
            except:
                logging.exception("DEV: Failed to write some config values")
            logging.debug("DEV: Config values have been set")
            with open(os.path.expandvars(config.CONFIG_LOC), "w", encoding="utf-8") as configfile:
                parser.write(configfile)
            logging.debug("DEV: Config has been written")
            self.wfile.write("<script>window.location=\"/end\";</script>".encode("utf8"))
        else:
            self._set_headers("text/html")
            index_loc = os.path.join(os.path.dirname(__file__), "website\index.html")
            with open(index_loc, "rb") as website:
                self.wfile.write(website.read())


class AuthenticationServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.path = ""
        server_address = ('localhost', 8080)
        self.httpd = HTTPServer(server_address, AuthenticationHandler)
        self.port = self.httpd.server_port

    def run(self):
        self.httpd.serve_forever()
