import os
import threading
import time
import uuid
import json
from flask import Flask, render_template, request, jsonify

# Import the refactored downloader modules
from fb_downloader import download_media
from pdf_downloader import download_flipbook

app = Flask(__name__)

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "output_dir": "",
    "theme": "dark"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except:
            pass
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

tasks = {}

def download_video(task_id, urls_text, browser, custom_name=None, mode="video"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    
    def log_cb(msg):
        tasks[task_id]["logs"].append(msg)

    for i, url in enumerate(urls):
        log_cb(f"[*] Processing ({i+1}/{len(urls)}) in {mode.upper()} mode: {url}")
        
        current_name = custom_name
        if custom_name and len(urls) > 1:
            current_name = f"{custom_name}_{i+1}"
        elif not custom_name and mode == "pdf":
            current_name = f"pdf_dl_{int(time.time())}_{i+1}"

        try:
            config = load_config()
            out_dir = config.get("output_dir", "").strip()
            
            if mode == "pdf":
                output_filename = f"{current_name}.pdf" if current_name else f"flipbook_{int(time.time())}.pdf"
                if out_dir:
                    output_filename = os.path.join(out_dir, output_filename)
                success = download_flipbook(url, output_filename, log_callback=log_cb)
            else:
                audio_only = (mode == "sound")
                
                # Apply output directory for yt-dlp by formatting custom_name with absolute path
                final_custom_name = current_name
                if out_dir:
                    if not final_custom_name:
                        final_custom_name = f"{out_dir}/%(title)s"
                    else:
                        final_custom_name = os.path.join(out_dir, final_custom_name)

                success = download_media(url, browser=browser, custom_name=final_custom_name, audio_only=audio_only, log_callback=log_cb)
                
            if not success:
                log_cb(f"[ERROR] Failed to download: {url}")
        except Exception as e:
            log_cb(f"[ERROR] Exception during download: {e}")
            
        if i < len(urls) - 1:
            log_cb("[*] Waiting 5 seconds before next download (Anti-bot)...")
            time.sleep(5)
            
    log_cb("[SUCCESS] All tasks finished!")
    tasks[task_id]["status"] = "finished"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.json
    urls_text = data.get("url", "")
    browser = data.get("browser", "chrome")
    custom_name = data.get("custom_name", "")
    mode = data.get("mode", "video")
    custom_cookies = data.get("custom_cookies", "")
    
    if custom_cookies:
        try:
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write(custom_cookies)
        except Exception as e:
            print(f"Error writing cookies: {e}")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running", "logs": []}
    
    thread = threading.Thread(target=download_video, args=(task_id, urls_text, browser, custom_name, mode))
    thread.start()
    
    return jsonify({"status": "started", "task_id": task_id})

@app.route("/api/logs")
def get_logs():
    task_id = request.args.get("task_id")
    task = tasks.get(task_id, {"logs": [], "status": "unknown"})
    return jsonify({"logs": task["logs"], "status": task["status"]})

@app.route("/api/config", methods=["GET", "POST"])
def handle_config():
    if request.method == "POST":
        data = request.json
        if data:
            save_config(data)
            return jsonify({"status": "success", "config": data})
        return jsonify({"status": "error", "message": "Invalid config data"}), 400
    
    return jsonify(load_config())

@app.route("/api/browse-folder", methods=["GET"])
def browse_folder():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Select Output Directory")
        root.destroy()
        if folder_path:
            # Convert forward slashes to backslashes for Windows aesthetics if desired
            folder_path = folder_path.replace('/', '\\')
            return jsonify({"path": folder_path})
        return jsonify({"path": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clear-cookies", methods=["POST"])
def clear_cookies():
    if os.path.exists("cookies.txt"):
        try:
            os.remove("cookies.txt")
            return jsonify({"status": "success", "message": "Cookies deleted successfully."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "success", "message": "No cookies file found."})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
