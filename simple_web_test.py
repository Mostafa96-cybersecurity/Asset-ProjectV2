#!/usr/bin/env python3
"""
Simple Web Service Test - Basic HTTP Server
"""
import http.server
import socketserver

PORT = 8080

class SimpleTestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
<!DOCTYPE html>
<html>
<head><title>Test Web Service</title></head>
<body>
    <h1>✅ Web Service Working!</h1>
    <p>This is a simple test to verify the web service can start and respond.</p>
    <p>If you can see this, the web service is working correctly.</p>
</body>
</html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"Request: {format % args}")

if __name__ == "__main__":
    print(f"Starting simple test server on port {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), SimpleTestHandler) as httpd:
            print(f"Server running at http://localhost:{PORT}")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Server error: {e}")