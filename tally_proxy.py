"""Local proxy that relays HTTP requests to Tally running inside a Parallels VM.

Uses a shared temp file to pass XML payloads to curl inside the VM,
avoiding shell escaping issues with XML special characters.
"""

import subprocess
import sys
import tempfile
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PRLCTL = "/Applications/Parallels Desktop.app/Contents/MacOS/prlctl"
VM_NAME = "Windows 11"
TALLY_VM_URL = "http://localhost:9000"
PROXY_PORT = 9000

# Shared directory accessible from both Mac and Windows VM via Parallels
# Mac path: ~/Desktop/tally_proxy_tmp/
# Windows path: \\Mac\Home\Desktop\tally_proxy_tmp\ (via Parallels shared folders)
SHARED_DIR = os.path.expanduser("~/Desktop/tally_proxy_tmp")
os.makedirs(SHARED_DIR, exist_ok=True)
SHARED_FILE = os.path.join(SHARED_DIR, "request.xml")
WIN_SHARED_FILE = r"\\Mac\Home\Desktop\tally_proxy_tmp\request.xml"


class TallyProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""

        # Write XML to shared file on Mac (visible to VM via Parallels sharing)
        with open(SHARED_FILE, "w", encoding="utf-8") as f:
            f.write(body)

        # Use curl inside the VM, reading body from the shared file
        cmd = [
            PRLCTL, "exec", VM_NAME, "cmd", "/c",
            f'curl -s -X POST -H "Content-Type: application/xml" '
            f'-d @{WIN_SHARED_FILE} {TALLY_VM_URL}'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            response_body = result.stdout.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(response_body)
        except subprocess.TimeoutExpired:
            self.send_response(504)
            self.end_headers()
            self.wfile.write(b"Tally request timed out")
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(b"<RESPONSE>Tally Proxy Running</RESPONSE>")

    def log_message(self, format, *args):
        print(f"[proxy] {args[0]}")
        sys.stdout.flush()


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    server = ReusableHTTPServer(("127.0.0.1", PROXY_PORT), TallyProxyHandler)
    print(f"Tally proxy running on http://127.0.0.1:{PROXY_PORT}")
    print(f"Relaying to Tally inside VM '{VM_NAME}' at {TALLY_VM_URL}")
    print(f"Shared file: {SHARED_FILE} -> {WIN_SHARED_FILE}")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped.")
        server.server_close()
