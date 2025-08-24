#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get('Content-Type')
        if not content_type or 'multipart/form-data' not in content_type:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request: Expected multipart/form-data\n")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
            }
        )

        # Find the uploaded file field (look for first item with a filename)
        uploaded_file = None
        filename = None

        if form.list:
            for field in form.list:
                if field.filename:
                    uploaded_file = field
                    filename = os.path.basename(field.filename)
                    break

        if uploaded_file is None:
            # If no filename given, fallback to first field data
            if form.list and form.list[0].file:
                uploaded_file = form.list[0]
                filename = "uploaded_file"
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No file uploaded\n")
                return

        # Save file to disk
        with open(filename, 'wb') as f:
            f.write(uploaded_file.file.read())

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"File uploaded successfully\n")
        print(f"[+] Saved uploaded file as: {filename} from {self.client_address[0]}")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Upload server running</h1></body></html>")

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8699
    print(f"Serving HTTP on {host} port {port} (http://{host}:{port}/) ...")
    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    httpd.serve_forever()
