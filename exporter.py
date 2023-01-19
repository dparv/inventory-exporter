#!/usr/bin/env python3
import sys
import json
import yaml
import socket
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


class Exporter(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        if self.path in ['/apt', '/snap', '/kernel']:
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
        elif self.path ==  '/kernel':
            self.wfile.write(self.generate_kernel_output().encode("utf-8"))
        else:
            helper= """
            <a href='/hostname'>/hostname</a>
            <br />
            <a href='/apt'>/apt</a>
            <br />
            <a href='/snap'>/snap</a>
            <br />
            <a href='/kernel'>/kernel</a>
            """
            self.wfile.write(helper.encode("utf-8"))

    def generate_apt_output(self):
        cmd = 'dpkg -l --admindir=/var/lib/snapd/hostfs/var/lib/dpkg'
        apts = subprocess.check_output(cmd.split())
        apts = str(apts)
        lines = apts.split('\\n')
        lines = lines[5:-1]
        output = []
        for line in lines:
            items = line.split()
            package = items[1]
            version = items[2]
            output.append({
                'package': package,
                'version': version,
                })
        return json.dumps(output)

    def generate_snap_output(self):
        cmd = 'snap list'
        snaps = subprocess.check_output(cmd.split())
        snaps = str(snaps)
        lines = snaps.split('\\n')
        lines = lines[1:-1]
        output = []
        for line in lines:
            items = line.split()
            snap = items[0]
            version = items[1]
            revision = items[2]
            tracking = items[3]
            output.append({
                'snap': snap,
                'version': version,
                'revision': revision,
                'tracking': tracking,
                })
        return json.dumps(output)

    def generate_kernel_output(self):
        cmd = 'uname -r'
        kernel = subprocess.check_output(cmd.split())
        kernel = kernel.splitlines()[0]
        output = {'kernel': str(kernel.decode())}
        return json.dumps(output)

def main():
    args = sys.argv
    if args[1] == "-c":
        config_file_path = args[2]
    else:
        sys.exit(1)
    config_file = open(config_file_path, 'r').read()
    config = yaml.safe_load(config_file)['settings']
    webServer = HTTPServer((config['bind_address'], config['port']), Exporter)
    webServer.serve_forever()


if __name__ == "__main__":        
    main()
