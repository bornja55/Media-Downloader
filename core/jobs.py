import os
import time
from abc import ABC, abstractmethod
from pdf_downloader import download_flipbook
from manga_downloader import download_manga
from fb_downloader import download_media

class DownloadJob(ABC):
    def __init__(self, task_id, url, custom_name, cookie_file, log_callback):
        self.task_id = task_id
        self.url = url
        self.custom_name = custom_name
        self.cookie_file = cookie_file
        self.log_cb = log_callback

    @abstractmethod
    def execute(self, out_dir):
        """Executes the download job. Must return True on success, False on failure."""
        pass

class FlipbookJob(DownloadJob):
    def execute(self, out_dir):
        self.log_cb(f"[*] Processing in PDF (Flipbook) mode: {self.url}")
        
        output_filename = f"{self.custom_name}.pdf" if self.custom_name else f"flipbook_{int(time.time())}.pdf"
        if out_dir:
            output_filename = os.path.join(out_dir, output_filename)
            
        return download_flipbook(self.url, output_filename, log_callback=self.log_cb, cookie_file=self.cookie_file)

class MangaChapterJob(DownloadJob):
    def __init__(self, task_id, url, custom_name, cookie_file, log_callback, package_format):
        super().__init__(task_id, url, custom_name, cookie_file, log_callback)
        self.package_format = package_format

    def execute(self, out_dir):
        self.log_cb(f"[*] Processing in IMAGE mode: {self.url}")
        
        out_dir_path = out_dir if out_dir else os.getcwd()
        has_cookies = self.cookie_file is not None and os.path.exists(self.cookie_file)
        
        # manga_downloader.download_manga doesn't return a boolean currently, we assume True if no exception
        try:
            download_manga(self.url, self.log_cb, None, self.custom_name, has_cookies, out_dir_path, self.package_format, cookie_file=self.cookie_file)
            return True
        except Exception as e:
            self.log_cb(f"[ERROR] MangaChapterJob exception: {e}")
            return False

class VideoJob(DownloadJob):
    def __init__(self, task_id, url, custom_name, cookie_file, log_callback, browser, audio_only):
        super().__init__(task_id, url, custom_name, cookie_file, log_callback)
        self.browser = browser
        self.audio_only = audio_only

    def execute(self, out_dir):
        mode_str = "SOUND" if self.audio_only else "VIDEO"
        self.log_cb(f"[*] Processing in {mode_str} mode: {self.url}")
        
        final_custom_name = self.custom_name
        if out_dir:
            if not final_custom_name:
                final_custom_name = f"{out_dir}/%(title)s"
            else:
                final_custom_name = os.path.join(out_dir, final_custom_name)

        return download_media(self.url, browser=self.browser, custom_name=final_custom_name, audio_only=self.audio_only, log_callback=self.log_cb, cookie_file=self.cookie_file)

class JobFactory:
    @staticmethod
    def create_job(task_id, url, mode, custom_name, cookie_file, log_callback, package_format="raw", browser="chrome"):
        if mode == "pdf":
            return FlipbookJob(task_id, url, custom_name, cookie_file, log_callback)
        elif mode == "image":
            return MangaChapterJob(task_id, url, custom_name, cookie_file, log_callback, package_format)
        else:
            audio_only = (mode == "sound")
            return VideoJob(task_id, url, custom_name, cookie_file, log_callback, browser, audio_only)
