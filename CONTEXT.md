# Domain Glossary

## Media Engine
- **Job**: A single download task originating from one URL.
- **Manga Chapter**: A specific webpage containing a sequence of images representing one chapter of a comic/manga. Represents a single Job in the system.

- **CBZ Format**: Comic Book Archive (essentially a renamed .zip file) containing a sequence of images. The standard output format for Manga Chapters.
- **Auto-Discovery**: A mechanism to detect the URL of the next chapter either by finding a 'Next' UI button or interpolating URL patterns, outputting suggestions to the Terminal.

- **Generic Image Hunter**: A scraping strategy that simulates user scrolling to trigger lazy-loading, extracting all large <img> tags (e.g. >400px width/height), serving as a universal fallback for typical manga sites.

## Universal RPA Screen Scraper
- **Analog Hole Macro**: A scraping mechanism that captures pixel data directly from the display monitor instead of extracting the source files, completely bypassing application-layer DRM.
- **Visual Capture**: The process of taking screenshots and packaging them into visual reading formats (PDF/CBZ) without extracting or analyzing the underlying text (No OCR).
- **Trigger Config**: A setting defining how the RPA bot advances to the next page, which can be a keypress (e.g. Right Arrow) or a custom X, Y coordinate for a mouse click.
- **Bounding Box**: A specific defined rectangular area (X, Y, Width, Height) on the screen to be captured, discarding the rest of the desktop (e.g. taskbars, reader UI).
- **Auto-Stop via Similarity**: A mechanism that stops the macro loop automatically when two consecutive captured images are identical, indicating the end of the book.
