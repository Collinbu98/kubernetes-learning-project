import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = socket.gethostname()

        if self.path == "/health":
            body = b"healthy\n"
        else:
            body = f"Media Platform API\nPod: {hostname}\n".encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = HTTPServer(("0.0.0.0", 8080), Handler)
print(f"API listening on port 8080 - {socket.gethostname()}")
server.serve_forever()
