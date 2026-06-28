import sys
import os

# Subprocess Hook for gallery-dl (PyInstaller Support)
if "--gdl" in sys.argv:
    import gallery_dl
    sys.argv.remove("--gdl")
    sys.exit(gallery_dl.main())

import threading
import time
import uuid
import json
import subprocess
from flask import Flask, render_template, request, jsonify

# Import the refactored downloader modules
from fb_downloader import download_media
from pdf_downloader import download_flipbook
from manga_downloader import download_manga
from rpa_downloader import get_monitors, capture_mouse_position, capture_screen_base64, start_rpa_task

# Support for PyInstaller
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
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

def download_video(task_id, urls_text, browser, custom_name=None, mode="video", package_format="raw", cookie_file=None):
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
                success = download_flipbook(url, output_filename, log_callback=log_cb, cookie_file=cookie_file)
            elif mode == "image":
                out_dir_path = out_dir if out_dir else os.getcwd()
                has_cookies = cookie_file is not None and os.path.exists(cookie_file)
                download_manga(url, log_cb, None, current_name, has_cookies, out_dir_path, package_format, cookie_file=cookie_file)
                success = True
            else:
                audio_only = (mode == "sound")
                
                # Apply output directory for yt-dlp by formatting custom_name with absolute path
                final_custom_name = current_name
                if out_dir:
                    if not final_custom_name:
                        final_custom_name = f"{out_dir}/%(title)s"
                    else:
                        final_custom_name = os.path.join(out_dir, final_custom_name)

                success = download_media(url, browser=browser, custom_name=final_custom_name, audio_only=audio_only, log_callback=log_cb, cookie_file=cookie_file)
                
            if not success:
                log_cb(f"[ERROR] Failed to download: {url}")
        except Exception as e:
            log_cb(f"[ERROR] Exception during download: {e}")
            
        if i < len(urls) - 1:
            log_cb("[*] Waiting 5 seconds before next download (Anti-bot)...")
            time.sleep(5)
            
    if cookie_file and os.path.exists(cookie_file):
        try:
            os.remove(cookie_file)
        except:
            pass

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
    package_format = data.get("package_format", "raw")
    
    task_id = str(uuid.uuid4())
    cookie_file = None

    if custom_cookies:
        try:
            cookie_file = f"cookies_{task_id}.txt"
            with open(cookie_file, "w", encoding="utf-8") as f:
                f.write(custom_cookies)
        except Exception as e:
            print(f"Error writing cookies: {e}")

    tasks[task_id] = {"status": "running", "logs": []}
    
    thread = threading.Thread(target=download_video, args=(task_id, urls_text, browser, custom_name, mode, package_format, cookie_file))
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

@app.route("/api/rpa/monitors")
def api_rpa_monitors():
    try:
        monitors = get_monitors()
        return jsonify({"status": "success", "monitors": monitors})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/rpa/capture_mouse", methods=["POST"])
def api_rpa_capture_mouse():
    try:
        pos = capture_mouse_position()
        return jsonify({"status": "success", "position": pos})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/rpa/preview", methods=["POST"])
def api_rpa_preview():
    try:
        data = request.json or {}
        monitor_id = data.get("monitor_id", 1)
        crop_box = data.get("crop_box")
        img_b64 = capture_screen_base64(monitor_id=monitor_id, crop_box=crop_box)
        return jsonify({"status": "success", "image": img_b64})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/rpa/launch_browser", methods=["POST"])
def api_rpa_launch_browser():
    try:
        import os, tempfile, shutil
        temp_dir = os.path.join(tempfile.gettempdir(), "rpa_browser_profile")
        
        browser_path = shutil.which("chrome") or shutil.which("google-chrome")
        if not browser_path:
            # Check common Windows paths for Chrome and Edge
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ]
            for p in paths:
                if os.path.exists(p):
                    browser_path = p
                    break
                    
        if browser_path:
            # Use --user-data-dir to force a completely new process that isn't attached to an already running, hardware-accelerated browser
            cmd = [browser_path, "--disable-gpu", "--disable-software-rasterizer", f"--user-data-dir={temp_dir}", "https://www.mebmarket.com"]
            subprocess.Popen(cmd)
            return jsonify({"status": "success", "message": f"Launched {os.path.basename(browser_path)} in Bypass Mode"})
        else:
            # Fallback
            subprocess.Popen(f'start msedge --disable-gpu --user-data-dir="{temp_dir}" "https://www.mebmarket.com"', shell=True)
            return jsonify({"status": "success", "message": "Attempted to launch Edge via shell"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def rpa_task_wrapper(task_id, config):
    def progress_cb(msg):
        tasks[task_id]["logs"].append(msg)
    def check_cancel():
        return tasks[task_id].get("cancel", False)
        
    try:
        result = start_rpa_task(config, progress_callback=progress_cb, check_cancel=check_cancel)
        if result.get("status") == "success":
            progress_cb(f"[SUCCESS] RPA finished. Saved {result.get('pages')} pages to {result.get('file')}")
        else:
            progress_cb(f"[ERROR] RPA Error: {result.get('message')}")
    except Exception as e:
        progress_cb(f"[ERROR] RPA Exception: {e}")
    finally:
        tasks[task_id]["status"] = "finished"

@app.route("/api/rpa/start", methods=["POST"])
def api_rpa_start():
    config = request.json or {}
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running", "logs": []}
    
    global_config = load_config()
    out_dir = global_config.get("output_dir", "").strip()
    if out_dir:
        config["output_dir"] = out_dir
        
    thread = threading.Thread(target=rpa_task_wrapper, args=(task_id, config))
    thread.start()
    
    return jsonify({"status": "started", "task_id": task_id})

if __name__ == "__main__":
    def open_browser():
        import webbrowser
        webbrowser.open_new("http://127.0.0.1:5000")
        
    # Open the browser after 2 seconds
    threading.Timer(2.0, open_browser).start()
    
    # Run the app (Turn off debug mode for production/PyInstaller to avoid opening two tabs)
    app.run(port=5000, debug=False)
