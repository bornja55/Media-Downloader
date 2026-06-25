import sys
import os
import argparse
import yt_dlp
import socket
import json
import urllib.request

# --- Monkeypatch socket.getaddrinfo to bypass corporate DNS via Google DoH ---
_orig_getaddrinfo = socket.getaddrinfo

def _doh_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host and ('youtube.com' in host or 'googlevideo.com' in host or 'youtu.be' in host):
        try:
            req = urllib.request.Request(f"https://dns.google/resolve?name={host}&type=A")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if 'Answer' in data:
                    for ans in data['Answer']:
                        if ans['type'] == 1: # A record (IPv4)
                            ip = ans['data']
                            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]
        except Exception:
            pass
    return _orig_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = _doh_getaddrinfo
# ------------------------------------------------------------------------------

class NativeLogger:
    def __init__(self, callback):
        self.callback = callback

    def debug(self, msg):
        # yt-dlp sends normal logs as debug
        if not msg.startswith('[debug] '):
            self.callback(msg)

    def warning(self, msg):
        self.callback(f"[WARNING] {msg}")

    def error(self, msg):
        self.callback(f"[ERROR] {msg}")

def download_media(url, browser="chrome", custom_name=None, audio_only=False, log_callback=print):
    def progress_hook(d):
        if d['status'] == 'downloading':
            # Reduce spam by only logging occasionally or just let logger handle it
            pass
        elif d['status'] == 'finished':
            log_callback(f"[SUCCESS] Download finished")

    try:
        log_callback(f"[*] Extracting URL: {url}")
        
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'noplaylist': True,
            'js_runtimes': {'node': {}},
            'remote_components': ['ejs:github'],
            'retries': 10,
            'fragment_retries': 10,
            'logger': NativeLogger(log_callback),
            'progress_hooks': [progress_hook],
        }
        
        cookie_file = "cookies.txt"
        if os.path.exists(cookie_file):
            log_callback(f"[*] Authenticating using cookie file: {cookie_file}...")
            ydl_opts['cookiefile'] = cookie_file
        elif browser:
            log_callback(f"[*] Authenticating using {browser} cookies...")
            ydl_opts['cookiesfrombrowser'] = (browser, )

        if audio_only:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
            if custom_name:
                ydl_opts['outtmpl'] = f'{custom_name}.%(ext)s'
            else:
                ydl_opts['outtmpl'] = '%(title)s.%(ext)s'
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
            if custom_name:
                ydl_opts['outtmpl'] = f'{custom_name}.%(ext)s'
            else:
                ydl_opts['outtmpl'] = '%(title)s.%(ext)s'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        log_callback("[+] Download completed successfully!")
        return True

    except Exception as e:
        log_callback(f"[-] An error occurred: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Media using yt-dlp with browser cookies.")
    parser.add_argument("url", help="The URL of the video to download")
    parser.add_argument("-b", "--browser", default="chrome", choices=["chrome", "firefox", "edge", "opera", "safari", "brave"], help="Browser to extract cookies from (default: chrome)")
    parser.add_argument("-n", "--name", help="Custom output filename (without extension)")
    parser.add_argument("-a", "--audio", action="store_true", help="Download audio only (mp3)")

    args = parser.parse_args()
    download_media(args.url, args.browser, args.name, args.audio)
