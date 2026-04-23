import os
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse, parse_qs

PORT = 8080
tasks = {}

def load_env():
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

def ark_request(method, path, api_key, body=None):
    url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks{path}"
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except HTTPError as e:
        return e.code, json.loads(e.read())

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default access log

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path
        qs = parse_qs(p.query)

        if path in ("/", "/index.html"):
            self._serve_file("static/index.html", "text/html; charset=utf-8")

        elif path == "/api/config":
            has_key = bool(os.environ.get("API_KEY", "").strip())
            self.send_json(200, {"has_server_key": has_key})

        elif path.startswith("/api/status/"):
            task_id = path[len("/api/status/"):]
            server_key = os.environ.get("API_KEY", "").strip()
            api_key = server_key or (qs.get("api_key", [""])[0])
            code, data = ark_request("GET", f"/{task_id}", api_key)
            if code != 200:
                self.send_json(code, data)
                return
            task_status = data.get("status", "")
            if task_status == "succeeded":
                video_url = None
                for item in data.get("content", []):
                    if item.get("type") == "video_url":
                        video_url = item.get("video_url", {}).get("url")
                        break
                local_path = None
                if video_url:
                    local_path = f"output/{task_id}.mp4"
                    if not os.path.exists(local_path):
                        os.makedirs("output", exist_ok=True)
                        req = Request(video_url)
                        with urlopen(req, timeout=120) as r:
                            with open(local_path, "wb") as f:
                                f.write(r.read())
                self.send_json(200, {"status": task_status, "local_path": local_path})
            elif task_status == "failed":
                error = data.get("error", {}).get("message", "Unknown error")
                self.send_json(200, {"status": task_status, "error": error})
            else:
                self.send_json(200, {"status": task_status})

        elif path.startswith("/api/video/"):
            task_id = path[len("/api/video/"):]
            file_path = f"output/{task_id}.mp4"
            if not os.path.exists(file_path):
                self.send_response(404); self.end_headers(); return
            with open(file_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", len(data))
            self.send_header("Content-Disposition", f'attachment; filename="{task_id}.mp4"')
            self.end_headers()
            self.wfile.write(data)

        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path == "/api/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            server_key = os.environ.get("API_KEY", "").strip()
            api_key = server_key or body.get("api_key", "")
            payload = {
                "model": body["model"],
                "content": [{"type": "text", "text": body["prompt"]}],
                "parameters": {
                    "resolution": body.get("resolution", "1280x720"),
                    "duration": int(body.get("duration", 5)),
                },
            }
            if body.get("image_url"):
                payload["content"].append(
                    {"type": "image_url", "image_url": {"url": body["image_url"]}}
                )
            code, data = ark_request("POST", "", api_key, payload)
            if code != 200:
                self.send_json(code, data)
                return
            task_id = data.get("id") or data.get("task_id")
            tasks[task_id] = {"prompt": body["prompt"], "model": body["model"]}
            self.send_json(200, {"task_id": task_id})
        else:
            self.send_response(404); self.end_headers()

    def _serve_file(self, file_path, content_type):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404); self.end_headers()


if __name__ == "__main__":
    load_env()
    os.makedirs("output", exist_ok=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"Seedance UI 已启动：{url}")
    print("关闭此窗口即可停止服务。")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
