import os
import httpx
from flask import Flask, request, jsonify, send_from_directory, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")

tasks = {}

ARK_BASE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/config")
def config():
    server_key = os.environ.get("API_KEY", "").strip()
    return jsonify({"has_server_key": bool(server_key)})


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    server_key = os.environ.get("API_KEY", "").strip()
    api_key = server_key or data.get("api_key", "")
    model = data.get("model", "")
    prompt = data.get("prompt", "")
    duration = int(data.get("duration", 5))
    resolution = data.get("resolution", "1280x720")
    image_url = data.get("image_url", "")

    content = [{"type": "text", "text": prompt}]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    payload = {
        "model": model,
        "content": content,
        "parameters": {
            "resolution": resolution,
            "duration": duration,
        },
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    resp = httpx.post(ARK_BASE, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    task_id = result.get("id") or result.get("task_id")
    tasks[task_id] = {"prompt": prompt, "model": model}
    return jsonify({"task_id": task_id})


@app.route("/api/status/<task_id>")
def status(task_id):
    server_key = os.environ.get("API_KEY", "").strip()
    api_key = server_key or request.args.get("api_key", "")

    headers = {"Authorization": f"Bearer {api_key}"}
    resp = httpx.get(f"{ARK_BASE}/{task_id}", headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    task_status = data.get("status", "")

    if task_status == "succeeded":
        video_url = None
        content = data.get("content", [])
        for item in content:
            if item.get("type") == "video_url":
                video_url = item.get("video_url", {}).get("url")
                break

        local_path = None
        if video_url:
            local_path = f"output/{task_id}.mp4"
            if not os.path.exists(local_path):
                video_resp = httpx.get(video_url, timeout=120, follow_redirects=True)
                video_resp.raise_for_status()
                os.makedirs("output", exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(video_resp.content)

        return jsonify({"status": task_status, "local_path": local_path})

    if task_status == "failed":
        error = data.get("error", {}).get("message", "Unknown error")
        return jsonify({"status": task_status, "error": error})

    return jsonify({"status": task_status})


@app.route("/api/video/<task_id>")
def video(task_id):
    path = f"output/{task_id}.mp4"
    return send_file(path, mimetype="video/mp4")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
