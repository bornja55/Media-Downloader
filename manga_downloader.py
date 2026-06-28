import os
import sys
import subprocess
import threading
import uuid
import time
import shutil
import zipfile

def download_manga(url, log_callback, update_progress, custom_name, has_cookies, output_dir, package_format, cookie_file=None):
    # Ensure gallery-dl downloads the entire post if a single photo URL is provided
    if "facebook.com" in url and "photo" in url and "set=" in url and "&setextract" not in url:
        url += "&setextract"
        log_callback("[*] Detected a single photo URL. Auto-upgrading to download the ENTIRE post/album!")

    log_callback(f"[*] Starting Image/Manga download for: {url}")
    
    # Determine the gallery-dl command
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        cmd = [sys.executable, "--gdl"]
    else:
        cmd = [sys.executable, "-m", "gallery_dl"]
        
    is_pdf = (package_format == 'pdf')
    is_cbz = (package_format == 'cbz')
    is_raw = (package_format == 'raw')
    
    # 1. Determine base name and directories
    unique_id = uuid.uuid4().hex[:8]
    if custom_name:
        base_name = custom_name
    else:
        # Fallback name: Try to extract an ID from the URL
        import re
        extracted_id = ""
        # Look for fbid=..., set=..., pcb..., or /posts/12345
        match = re.search(r'(?:fbid=|set=p?c?b?\.?|/posts/|/permalink/)(\d+)', url)
        if match:
            extracted_id = match.group(1)
        
        if extracted_id:
            base_name = f"FB_{extracted_id}"
        else:
            base_name = f"Export_{int(time.time())}_{unique_id}"
        
    if is_raw:
        # Raw images go directly to a dedicated folder inside output_dir so they never mix
        exact_dir = os.path.join(output_dir, base_name)
    else:
        # PDF and CBZ download to a temporary folder, which gets zipped/compiled, then deleted
        exact_dir = os.path.join(output_dir, f"temp_dl_{unique_id}")
        
    cmd.extend(["-D", exact_dir])
    
    # 2. Filename template (must include {num} to prevent overwriting!)
    if is_raw:
        cmd.extend(["--filename", f"image_{'{num:03d}'}.{'{extension}'}"])
        log_callback(f"[*] Raw Mode: Saving images into folder: {exact_dir}")
    elif is_cbz:
        cmd.extend(["--filename", f"image_{'{num:03d}'}.{'{extension}'}"])
        log_callback("[*] Manga Mode: Images will be packaged into a .cbz comic book.")
    elif is_pdf:
        cmd.extend(["--filename", f"image_{'{num:03d}'}.{'{extension}'}"])
        log_callback("[*] Document Mode: Images will be compiled into a .pdf file.")
    
    if has_cookies and cookie_file:
        cookie_path = os.path.join(os.getcwd(), cookie_file)
        if os.path.exists(cookie_path):
            cmd.extend(["--cookies", cookie_path])
            log_callback(f"[*] Using Custom Cookies ({cookie_file}) for authentication.")
            
    cmd.append(url)
    
    try:
        # Start the subprocess
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Read output line by line
        for line in process.stdout:
            line = line.strip()
            if line:
                log_callback(f"[gallery-dl] {line}")
                
        process.wait()
        
        if process.returncode == 0:
            if is_pdf or is_cbz:
                log_callback(f"[*] Download complete. Compiling into {'.pdf' if is_pdf else '.cbz'}...")
                try:
                    images = []
                    for root, _, files in os.walk(exact_dir):
                        for f in files:
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                                images.append(os.path.join(root, f))
                    
                    images.sort()
                    
                    if images:
                        if is_pdf:
                            try:
                                import img2pdf
                                pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
                                with open(pdf_path, "wb") as f:
                                    f.write(img2pdf.convert(images))
                                log_callback(f"[SUCCESS] Saved to: {pdf_path}")
                            except ImportError:
                                log_callback("[ERROR] Required library (img2pdf) is missing. Cannot convert to PDF. Falling back to .cbz...")
                                is_cbz = True
                        
                        if is_cbz:
                            cbz_path = os.path.join(output_dir, f"{base_name}.cbz")
                            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                for idx, img_path in enumerate(images):
                                    # Add to zip with a clean ordered name
                                    ext = os.path.splitext(img_path)[1]
                                    arcname = f"page_{idx+1:03d}{ext}"
                                    zipf.write(img_path, arcname)
                            log_callback(f"[SUCCESS] Saved to: {cbz_path}")
                    else:
                        log_callback("[ERROR] No valid images found to compile.")
                except Exception as e:
                    log_callback(f"[ERROR] Failed to create package: {str(e)}")
                finally:
                    # Clean up temporary directory
                    if os.path.exists(exact_dir):
                        shutil.rmtree(exact_dir, ignore_errors=True)
            else:
                log_callback(f"[SUCCESS] Saved to: {exact_dir}")
        else:
            log_callback(f"[ERROR] Process exited with code {process.returncode}")
            
    except Exception as e:
        log_callback(f"[ERROR] An exception occurred: {str(e)}")
