from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8000

STATUS = "OFF"


def render_page():
    status_class = "on" if STATUS == "ON" else "off"

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Статус кнопки</title>
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    <main class="panel">
      <h1>Статус кнопки</h1>

      <div class="status {status_class}">
        <span>{STATUS}</span>
      </div>

      <div class="controls">
        <a href="/status_on">ON</a>
        <a href="/status_off">OFF</a>
      </div>
    </main>
  </body>
</html>"""


def send_text(handler, content_type, body):
    encoded_body = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(encoded_body)))
    handler.end_headers()
    handler.wfile.write(encoded_body)


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global STATUS

        path = urlparse(self.path).path

        if path == "/styles.css":
            css = Path("styles.css").read_text(encoding="utf-8")
            send_text(self, "text/css; charset=utf-8", css)
            return

        if path == "/":
            send_text(self, "text/html; charset=utf-8", render_page())
            return

        if path == "/status":
            send_text(self, "text/plain; charset=utf-8", STATUS)
            return

        if path in ("/status_on", "/button_on", "/knopka_on"):
            STATUS = "ON"
            self.redirect_home()
            return

        if path in ("/status_off", "/button_off", "/knopka_off"):
            STATUS = "OFF"
            self.redirect_home()
            return

        self.send_error(404)

    def redirect_home(self):
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), StatusHandler)
    print(f"Сервер запущен: http://{HOST}:{PORT}")
    server.serve_forever()
