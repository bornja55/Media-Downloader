import os
import zipfile
import shutil

class ArchiveAdapter:
    """
    Adapter for converting a folder of images into CBZ or PDF formats.
    This creates a clean seam separating download logic from archiving logic.
    """
    
    @staticmethod
    def _get_valid_images(image_folder):
        images = []
        for root, _, files in os.walk(image_folder):
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    images.append(os.path.join(root, f))
        images.sort()
        return images

    @staticmethod
    def pack_to_pdf(image_folder, output_path, log_callback=print):
        """Compiles images in the given folder into a PDF."""
        images = ArchiveAdapter._get_valid_images(image_folder)
        if not images:
            log_callback("[ERROR] No valid images found to compile into PDF.")
            return False
            
        try:
            import img2pdf
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(images))
            log_callback(f"[SUCCESS] Saved PDF to: {output_path}")
            return True
        except ImportError:
            log_callback("[ERROR] Required library (img2pdf) is missing. Cannot convert to PDF.")
            return False
        except Exception as e:
            log_callback(f"[ERROR] Failed to create PDF: {str(e)}")
            return False

    @staticmethod
    def pack_to_cbz(image_folder, output_path, log_callback=print):
        """Packages images in the given folder into a CBZ comic book archive."""
        images = ArchiveAdapter._get_valid_images(image_folder)
        if not images:
            log_callback("[ERROR] No valid images found to compile into CBZ.")
            return False
            
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for idx, img_path in enumerate(images):
                    # Add to zip with a clean ordered name
                    ext = os.path.splitext(img_path)[1]
                    arcname = f"page_{idx+1:03d}{ext}"
                    zipf.write(img_path, arcname)
            log_callback(f"[SUCCESS] Saved CBZ to: {output_path}")
            return True
        except Exception as e:
            log_callback(f"[ERROR] Failed to create CBZ: {str(e)}")
            return False
