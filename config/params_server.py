# params_sever.py is called from boot.py when boot is pushed at startup or if config.txt dont exist
# params_server.py launch a web server to store or change values inside config.txt
# Open browser and go to: http://192.168.4.1
# after the values are saved the esp will reboot (machine.reset) this will unload evrything
# from memory and esp will reboot fresh and main.py will start ans this time main.py will
# use params.py during run mode to read or write the credentials or variable in config.txt file


import network
import socket
import machine
import time

CONFIG_FILE = "/config/config.txt"
TOTAL_SLOTS = 10
AP_SSID = "sam"
AP_PASS = "12345678"


def _load_lines():
    lines = []
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                lines.append(line.rstrip("\n"))
    except OSError:
        pass
    while len(lines) < TOTAL_SLOTS * 2:
        slot = (len(lines) // 2) + 1
        lines.append("slot{}_empty".format(slot))
        lines.append("-")
    return lines


def _save_lines(lines):
    with open(CONFIG_FILE, "w") as f:
        for line in lines:
            f.write(line + "\n")


def _is_empty_slot(name, value):
    return name.endswith("_empty") or value == "-"


def _build_html(lines):
    fields_html = ""
    for i in range(0, TOTAL_SLOTS * 2, 2):
        name = lines[i]
        value = lines[i + 1]
        if _is_empty_slot(name, value):
            continue
        safe_value = value.replace('"', "&quot;")
        fields_html += """
        <div style="background:#2d2d2d;border-radius:12px;padding:14px 16px;border:0.5px solid #444;">
          <label style="color:#aaa;font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:0.6px;display:block;margin-bottom:8px;">{name}</label>
          <input type="text" name="slot{slot}" value="{value}"
            style="width:100%;background:#1a1a1a;border:0.5px solid #555;border-radius:8px;
                   padding:12px 14px;color:#fff;font-size:17px;box-sizing:border-box;outline:none;">
        </div>""".format(name=name, slot=(i // 2) + 1, value=safe_value)

    return """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta charset="UTF-8">
<title>ESP32 Config</title>
</head>
<body style="background:#1a1a1a;margin:0;padding:24px 16px;font-family:sans-serif;box-sizing:border-box;">
  <div style="text-align:center;margin-bottom:28px;">
    <div style="display:inline-block;background:#007AFF;border-radius:12px;padding:8px 18px;margin-bottom:12px;">
      <span style="color:#fff;font-size:13px;font-weight:500;letter-spacing:0.5px;">CONFIG MODE</span>
    </div>
    <h1 style="color:#ffffff;font-size:22px;font-weight:500;margin:0 0 4px;">ESP32 Parameters</h1>
    <p style="color:#888;font-size:13px;margin:0;">Edit values and tap Save</p>
  </div>
  <form method="POST" action="/save">
    <div style="display:flex;flex-direction:column;gap:14px;margin-bottom:28px;">
      {fields}
    </div>
    <button type="submit"
      style="width:100%;background:#007AFF;border:none;border-radius:14px;padding:18px;
             color:#fff;font-size:19px;font-weight:500;cursor:pointer;letter-spacing:0.3px;">
      Save &amp; Reboot
    </button>
  </form>
  <p style="color:#555;font-size:12px;text-align:center;margin-top:16px;">
    ESP32 will restart automatically after saving
  </p>
</body>
</html>""".format(fields=fields_html)


def _parse_post_body(body):
    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, _, val = pair.partition("=")
            val = val.replace("+", " ")
            decoded = ""
            j = 0
            while j < len(val):
                if val[j] == "%" and j + 2 < len(val):
                    try:
                        decoded += chr(int(val[j+1:j+3], 16))
                        j += 3
                    except Exception:
                        decoded += val[j]
                        j += 1
                else:
                    decoded += val[j]
                    j += 1
            params[key.strip()] = decoded
    return params


def _send_response(conn, status, content_type, body):
    body_bytes = body.encode("utf-8")
    response = "HTTP/1.1 {}\r\nContent-Type: {}; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\n\r\n".format(
        status, content_type, len(body_bytes)
    )
    conn.sendall(response.encode("utf-8"))
    conn.sendall(body_bytes)


def start_config_mode():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASS, authmode=network.AUTH_WPA_WPA2_PSK)

    while not ap.active():
        time.sleep(0.1)

    print("AP started — SSID: {} | IP: {}".format(AP_SSID, ap.ifconfig()[0]))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 80))
    server.listen(1)
    print("Web server listening on port 80")

    while True:
        conn, addr = server.accept()
        try:
            request = b""
            while True:
                chunk = conn.recv(1024)
                request += chunk
                if len(chunk) < 1024:
                    break

            request_str = request.decode("utf-8", "ignore")
            first_line = request_str.split("\r\n")[0]

            if first_line.startswith("POST /save"):
                if "\r\n\r\n" in request_str:
                    body = request_str.split("\r\n\r\n", 1)[1]
                else:
                    body = ""
                post_params = _parse_post_body(body)
                lines = _load_lines()
                for key, val in post_params.items():
                    if key.startswith("slot"):
                        try:
                            slot_num = int(key[4:])
                            if 1 <= slot_num <= TOTAL_SLOTS:
                                idx = (slot_num - 1) * 2 + 1
                                lines[idx] = val
                        except ValueError:
                            pass
                _save_lines(lines)
                saved_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="3;url=/">
</head>
<body style="background:#1a1a1a;margin:0;padding:40px 16px;font-family:sans-serif;text-align:center;">
  <div style="color:#34C759;font-size:60px;margin-bottom:16px;">&#10003;</div>
  <h1 style="color:#fff;font-size:22px;font-weight:500;">Saved!</h1>
  <p style="color:#888;font-size:14px;">Rebooting ESP32...</p>
</body></html>"""
                _send_response(conn, "200 OK", "text/html", saved_html)
                conn.close()
                time.sleep(1.5)
                machine.reset()

            else:
                lines = _load_lines()
                html = _build_html(lines)
                _send_response(conn, "200 OK", "text/html", html)

        except Exception as e:
            print("Server error:", e)
        finally:
            conn.close()
