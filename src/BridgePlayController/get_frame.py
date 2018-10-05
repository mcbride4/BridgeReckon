"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import os
from skimage import io
global snap_id


class S(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        global snap_id
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself
        data = json.loads(post_data)
        data['pi_id'] = 1
        for key, item in data.items():
            if 'id_' in key:
                os.makedirs('/home/dawid_rymarczyk/Pobrane/BridgeReckon-user_interface/src/flask/app/static/'
                            + str(data['pi_id']) + '/' + str(key) + '/', exist_ok=True)
                io.imsave('/home/dawid_rymarczyk/Pobrane/BridgeReckon-user_interface/src/flask/app/static/'
                          + str(data['pi_id']) + '/' + str(key) + '/' + str(snap_id) + '.png',
                          data[key]['img'])
        snap_id += 1
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=9001):
    # logging.basicConfig(level=logging.INFO)
    global snap_id
    snap_id = 0
    server_address = ('192.168.100.1', port)
    httpd = server_class(server_address, handler_class)
    # logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    # logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
