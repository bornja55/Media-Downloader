import mss
import pyautogui
import time
import base64
import os
import io
import tempfile
import zipfile
from PIL import Image, ImageChops
import numpy as np

def get_monitors():
    """Returns a list of available monitors."""
    monitors_info = []
    with mss.mss() as sct:
        # sct.monitors[0] is a dict of all monitors together.
        for i, monitor in enumerate(sct.monitors[1:], 1):
            monitors_info.append({
                "id": i,
                "name": f"Monitor {i}",
                "width": monitor["width"],
                "height": monitor["height"],
                "left": monitor["left"],
                "top": monitor["top"]
            })
    return monitors_info

def capture_mouse_position():
    """Waits 5 seconds and returns the current mouse position."""
    time.sleep(5)
    x, y = pyautogui.position()
    return {"x": int(x), "y": int(y)}

def capture_screen_base64(monitor_id=1, crop_box=None):
    """
    Captures the specified monitor. If crop_box is provided (x, y, w, h),
    crops the image. Returns base64 encoded jpeg.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[int(monitor_id)]
        
        if crop_box:
            capture_region = {
                "top": monitor["top"] + crop_box['y'],
                "left": monitor["left"] + crop_box['x'],
                "width": crop_box['w'],
                "height": crop_box['h']
            }
        else:
            capture_region = monitor
            
        sct_img = sct.grab(capture_region)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

def are_images_identical(img1, img2):
    """Returns True if the two PIL Images are identical."""
    if img1 is None or img2 is None:
        return False
    diff = ImageChops.difference(img1, img2)
    return not diff.getbbox()

def start_rpa_task(config, progress_callback=None, check_cancel=None):
    """
    Main RPA loop using pyautogui for Virtual Machine targeting.
    """
    monitor_id = int(config.get('monitor_id', 1))
    crop_box = config.get('crop_box')
    trigger_type = config.get('trigger_type', 'right')
    trigger_pos = config.get('trigger_pos')
    delay = float(config.get('delay', 1.5))
    max_pages = int(config.get('max_pages', 100))
    
    output_dir = config.get('output_dir', "rpa_output")
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = tempfile.mkdtemp()
    
    image_paths = []
    prev_image = None
    
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]
        if crop_box:
            capture_region = {
                "top": monitor["top"] + crop_box['y'],
                "left": monitor["left"] + crop_box['x'],
                "width": crop_box['w'],
                "height": crop_box['h']
            }
        else:
            capture_region = monitor
            
        if progress_callback:
            progress_callback("[System] Waiting 5 seconds for you to activate the VM window...")
        
        # Initial delay to let the user switch focus to VirtualBox
        for i in range(5, 0, -1):
            if check_cancel and check_cancel():
                break
            if progress_callback:
                progress_callback(f"Starting in {i}...")
            time.sleep(1)

        for page_num in range(1, max_pages + 1):
            if check_cancel and check_cancel():
                if progress_callback:
                    progress_callback(f"RPA Cancelled at page {page_num - 1}.")
                break
                
            # 1. Capture screen
            sct_img = sct.grab(capture_region)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            # 2. Check similarity (Auto-Stop)
            if prev_image and are_images_identical(prev_image, img):
                if progress_callback:
                    progress_callback(f"Auto-stop: Image didn't change on page {page_num}. End of book detected.")
                break
            
            # 3. Save image
            img_filename = os.path.join(temp_dir, f"page_{page_num:04d}.jpg")
            img.save(img_filename, "JPEG", quality=95)
            image_paths.append(img_filename)
            prev_image = img.copy()
            
            if progress_callback:
                progress_callback(f"Captured page {page_num}")
                
            # Check if we reached max_pages before clicking next
            if page_num >= max_pages:
                if progress_callback:
                    progress_callback(f"Reached max pages ({max_pages}). Stopping.")
                break
            
            # 4. Trigger next page via Windows OS (PyDirectInput/PyAutoGUI)
            # VirtualBox often ignores injected keyboard events from PyAutoGUI.
            # PyDirectInput uses DirectX Scan Codes which VirtualBox respects.
            try:
                if trigger_type == 'click' and trigger_pos:
                    pyautogui.click(x=trigger_pos['x'], y=trigger_pos['y'])
                else:
                    import pydirectinput
                    if trigger_type == 'right':
                        pydirectinput.press('right')
                    elif trigger_type == 'left':
                        pydirectinput.press('left')
                    elif trigger_type == 'space':
                        pydirectinput.press('space')
                    elif trigger_type == 'pagedown':
                        pydirectinput.press('pagedown')
            except Exception as e:
                if progress_callback:
                    progress_callback(f"[Error] PyAutoGUI failed: {e}")
                
            # 5. Delay
            time.sleep(delay)
            
    # Compile output
    if not image_paths:
        return {"status": "error", "message": "No images captured."}
        
    output_name = config.get('output_name', 'rpa_capture')
    if not output_name.strip():
        output_name = f"rpa_capture_{int(time.time())}"
        
    format_type = config.get('output_format', 'cbz').lower()
    
    if format_type == 'pdf':
        try:
            import img2pdf
            final_path = os.path.join(output_dir, f"{output_name}.pdf")
            with open(final_path, "wb") as f:
                f.write(img2pdf.convert(image_paths))
        except ImportError:
            format_type = 'cbz' # Fallback
            
    if format_type == 'cbz':
        final_path = os.path.join(output_dir, f"{output_name}.cbz")
        with zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for img_path in image_paths:
                zf.write(img_path, os.path.basename(img_path))
                
    # Cleanup temp images
    for p in image_paths:
        try:
            os.remove(p)
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass
        
    return {"status": "success", "file": final_path, "pages": len(image_paths)}
