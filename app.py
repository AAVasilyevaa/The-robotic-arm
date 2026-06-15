from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8000

HAND_STATE = {
    "button_pressed": False,
    "object_detected": False,
}


def yes_no(value):
    return "да" if value else "нет"


def get_state():
    button_pressed = HAND_STATE["button_pressed"] or HAND_STATE["object_detected"]
    object_detected = HAND_STATE["object_detected"]
    fingers_closed = button_pressed

    if not button_pressed:
        led = "не горит"
        result = "рука разжата"
        led_class = "off"
    elif object_detected:
        led = "зеленый"
        result = "предмет удерживается"
        led_class = "green"
    else:
        led = "красный"
        result = "ложное нажатие"
        led_class = "red"

    return {
        "button_pressed": button_pressed,
        "object_detected": object_detected,
        "fingers_closed": fingers_closed,
        "led": led,
        "result": result,
        "led_class": led_class,
    }


def render_state_lines(state):
    return [
        f"Кнопка нажата: {yes_no(state['button_pressed'])}",
        f"Предмет в руке: {yes_no(state['object_detected'])}",
        f"Пальцы сжаты: {yes_no(state['fingers_closed'])}",
        f"LED-индикатор: {state['led']}",
        f"Итог: {state['result']}",
    ]


def render_page():
    state = get_state()
    lines = render_state_lines(state)
    line_html = "\n".join(f"        <p>{line}</p>" for line in lines)

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Состояние руки-держателя</title>
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    <main class="panel">
      <h1>Состояние руки-держателя</h1>

      <div class="controls">
        <a href="/button_on">Кнопка: да</a>
        <a href="/button_off">Кнопка: нет</a>
        <a href="/object_on">Предмет: да</a>
        <a href="/object_off">Предмет: нет</a>
      </div>

      <section class="state {state['led_class']}">
{line_html}
      </section>

      <a class="status-link" href="/status">Открыть текстовый статус</a>
    </main>
  </body>
</html>"""


def set_header(handler, content_type, body):
    encoded_body = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(encoded_body)))
    handler.end_headers()
    handler.wfile.write(encoded_body)


class HandStateHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/styles.css":
            self.send_css()
            return

        if path == "/":
            self.send_page()
            return

        if path == "/status":
            self.send_status()
            return

        if path in ("/button_on", "/knopka_on"):
            HAND_STATE["button_pressed"] = True
            self.redirect_home()
            return

        if path in ("/button_off", "/knopka_off"):
            HAND_STATE["button_pressed"] = False
            HAND_STATE["object_detected"] = False
            self.redirect_home()
            return

        if path == "/object_on":
            HAND_STATE["object_detected"] = True
            HAND_STATE["button_pressed"] = True
            self.redirect_home()
            return

        if path == "/object_off":
            HAND_STATE["object_detected"] = False
            self.redirect_home()
            return

        if path == "/reset":
            HAND_STATE["button_pressed"] = False
            HAND_STATE["object_detected"] = False
            self.redirect_home()
            return

        self.send_error(404)

    def send_page(self):
        set_header(self, "text/html; charset=utf-8", render_page())

    def send_status(self):
        state_text = "\n".join(render_state_lines(get_state()))
        set_header(self, "text/plain; charset=utf-8", state_text)

    def send_css(self):
        css = Path("styles.css").read_text(encoding="utf-8")
        set_header(self, "text/css; charset=utf-8", css)

    def redirect_home(self):
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), HandStateHandler)
    print(f"Сервер запущен: http://{HOST}:{PORT}")
    server.serve_forever()
