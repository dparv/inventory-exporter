#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import subprocess

hostname = '0.0.0.0'
port = 8675

class Exporter(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        if self.path == '/apt' or self.path == '/snap':
            self.send_header('Content-type', 'application/json')
        else:
            self.send_header('Content-type', 'text/html')
        self.end_headers()    

    def do_GET(self):
        self._set_response()
        if self.path == '/hostname':
            self.wfile.write(socket.gethostname().encode("utf-8"))
        elif self.path == '/apt':
            self.wfile.write(self.generate_apt_output().encode("utf-8"))
        elif self.path ==  '/snap':
            self.wfile.write(self.generate_snap_output().encode("utf-8"))
        else:
            helper= """
            <a href='/hostname'>/hostname</a>
            <br />
            <a href='/apt'>/apt</a>
            <br />
            <a href='/snap'>/snap</a>
            """
            self.wfile.write(helper.encode("utf-8"))

    def generate_apt_output(self):
        cmd = 'dpkg -l'
        apts = subprocess.check_output(cmd.split())
        apts = str(apts)
        lines = apts.split('\\n')
        lines = lines[5:-1]
        export = []
        for line in lines:
            items = line.split()
            package = items[1]
            version = items[2]
            export.append({
                'package': package,
                'version': version,
                })
        return json.dumps(export)

    def generate_snap_output(self):
        cmd = 'snap list'
        snaps = subprocess.check_output(cmd.split())
        snaps = str(snaps)
        lines = snaps.split('\\n')
        lines = lines[1:-1]
        export = []
        for line in lines:
            items = line.split()
            snap = items[0]
            version = items[1]
            revision = items[2]
            tracking = items[3]
            export.append({
                'snap': snap,
                'version': version,
                'revision': revision,
                'tracking': tracking,
                })
        return json.dumps(export)


def main():
    webServer = HTTPServer((hostname, port), Exporter)
    webServer.serve_forever()


if __name__ == "__main__":        
    main()
