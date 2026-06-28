import io
import os
import re
import sys
import time
import argparse
import tempfile
from urllib.parse import urlparse, urljoin

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

def parse_fliphtml5_url(url: str) -> tuple[str, str | None]:
    parsed = urlparse(url.strip())
    if not parsed.hostname or "fliphtml5.com" not in parsed.hostname:
        return url, None

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) >= 3:
        doc_name = parts[2]
        clean_path = "/".join(parts[:2])
        scheme = parsed.scheme or "https"
        clean_url = f"{scheme}://{parsed.hostname}/{clean_path}/"
        return clean_url, doc_name
    elif len(parts) == 2:
        return url.strip(), None
    return url.strip(), None


def resolve_online_url(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    
    if "fliphtml5.com" in hostname and "online.fliphtml5.com" not in hostname:
        path = parsed.path.rstrip("/") + "/"
        return f"https://online.fliphtml5.com{path}"
    
    if "anyflip.com" in hostname and "online.anyflip.com" not in hostname:
        path = parsed.path.rstrip("/") + "/"
        return f"https://online.anyflip.com{path}"
    
    return url


def download_flipbook(url: str, output_pdf: str, max_pages: int = 999, wait_load: float = 8.0, headless: bool = True, log_callback=print, cookie_file=None):
    try:
        log_callback(f"[*] Analyzing URL: {url}")
        
        parsed = urlparse(url)
        hostname = parsed.hostname.lower() if parsed.hostname else ""
        
        if "fliphtml5.com" in hostname and "online.fliphtml5.com" not in hostname:
            log_callback("[*] Flipbook detected -> opening online version directly")
            clean_url, doc_name = parse_fliphtml5_url(url)
            parsed_clean = urlparse(clean_url)
            path = parsed_clean.path.rstrip("/") + "/"
            base_url = f"https://online.fliphtml5.com{path}"
        elif "anyflip.com" in hostname and "online.anyflip.com" not in hostname:
            log_callback("[*] Flipbook detected -> opening online version directly")
            path = parsed.path.rstrip("/") + "/"
            base_url = f"https://online.anyflip.com{path}"
        else:
            base_url = url.rstrip('/') + '/'

        options = Options()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=0")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        log_callback("[*] Preparing Chrome Driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        page_data = None
        total_pages = 0
        try:
            log_callback(f"[*] Opening: {base_url}")
            driver.get(base_url)
            
            if cookie_file and os.path.exists(cookie_file):
                try:
                    import http.cookiejar
                    cj = http.cookiejar.MozillaCookieJar(cookie_file)
                    cj.load(ignore_discard=True, ignore_expires=True)
                    for cookie in cj:
                        driver.add_cookie({
                            'name': cookie.name,
                            'value': cookie.value,
                            'domain': cookie.domain,
                            'path': cookie.path
                        })
                    log_callback(f"[*] Injected cookies from {cookie_file} into Selenium.")
                    driver.refresh()
                    time.sleep(2)
                except Exception as e:
                    log_callback(f"[WARNING] Could not inject cookies: {e}")
            
            log_callback(f"[*] Waiting {wait_load:.0f}s for page to load...")
            time.sleep(wait_load)

            log_callback("[*] Extracting page data...")
            doc_title = driver.title.strip()
            log_callback(f"[*] Document Title: {doc_title}")
            page_data = driver.execute_script("try { return fliphtml5_pages || pages || window.bookConfig.pages; } catch(e) { return null; }")
            
            try:
                total_pages = int(driver.execute_script("return typeof totalPageCount !== 'undefined' ? totalPageCount : (typeof totalPages !== 'undefined' ? totalPages : 0);"))
            except:
                total_pages = len(page_data) if page_data else 0

            if not page_data and total_pages > 0:
                log_callback("[-] Could not extract page data (JSON), but found page count.")
            elif page_data:
                total_pages = len(page_data)
                log_callback(f"[*] Found {total_pages} pages!")
            else:
                log_callback("[-] ERROR: Could not determine pages.")
                return False
        finally:
            try:
                driver.quit()
                log_callback("[*] Chrome closed. Proceeding to HTTP download...")
            except:
                pass

        if not page_data:
            log_callback("[-] ERROR: Could not extract page data.")
            return False

        session = requests.Session()
        
        if cookie_file and os.path.exists(cookie_file):
            import http.cookiejar
            cj = http.cookiejar.MozillaCookieJar(cookie_file)
            try:
                cj.load(ignore_discard=True, ignore_expires=True)
                session.cookies.update(cj)
                log_callback(f"[*] Loaded cookies from {cookie_file} into requests session.")
            except Exception as e:
                log_callback(f"[WARNING] Could not load cookies from {cookie_file}: {e}")

        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": url,
        })

        actual_max = min(total_pages, max_pages)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_files = []
            for i, page_info in enumerate(page_data[:actual_max]):
                page_num = i + 1
                img_url = None
                for key in ["n", "l"]:
                    if isinstance(page_info, dict) and key in page_info and page_info[key]:
                        val = page_info[key]
                        if isinstance(val, list): val = val[0]
                        raw = str(val).lstrip("./")
                        if not raw.startswith("files/"): raw = f"files/large/{raw}"
                        img_url = urljoin(base_url, raw)
                        break

                if not img_url:
                    log_callback(f"[-] Page {page_num}: No image URL found")
                    continue

                try:
                    resp = session.get(img_url, timeout=30)
                    resp.raise_for_status()
                    img_path = os.path.join(temp_dir, f"page_{page_num:04d}.jpg")
                    with open(img_path, 'wb') as f: f.write(resp.content)
                    temp_files.append(img_path)
                    log_callback(f"[*] Page {page_num}/{actual_max} downloaded")
                except Exception as e:
                    log_callback(f"[-] Page {page_num}: Download failed - {e}")

            if temp_files:
                log_callback(f"[*] Combining {len(temp_files)} pages into PDF...")
                
                if "pdf_dl_" in os.path.basename(output_pdf) and doc_title:
                    import re
                    safe_title = re.sub(r'[\\/*?:"<>|]', "", doc_title).strip()
                    if safe_title:
                        output_pdf = os.path.join(os.path.dirname(output_pdf), f"{safe_title}.pdf")
                
                os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or '.', exist_ok=True)
                first_image = Image.open(temp_files[0]).convert("RGB")
                other_images = [Image.open(f).convert("RGB") for f in temp_files[1:]]
                first_image.save(output_pdf, save_all=True, append_images=other_images, resolution=150.0, quality=95)
                log_callback(f"[SUCCESS] Saved to: {os.path.abspath(output_pdf)}")
                return True
            return False
    except Exception as exc:
        log_callback(f"[-] ERROR: {exc}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download Flipbooks to PDF")
    parser.add_argument("url", help="The URL of the flipbook")
    parser.add_argument("-n", "--name", default="flipbook_output", help="Custom output filename (without extension)")
    args = parser.parse_args()
    output_filename = f"{args.name}.pdf"
    clean_url, doc_name = parse_fliphtml5_url(args.url)
        
    if doc_name and args.name == "flipbook_output":
        safe_name = doc_name.replace("_", " ").strip()
        output_filename = f"{safe_name}.pdf"

    download_flipbook(args.url, output_filename)

if __name__ == "__main__":
    main()
