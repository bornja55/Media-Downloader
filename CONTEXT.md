# Domain Glossary

## Media Engine
- **Job**: A single download task originating from one URL.
- **Manga Chapter**: A specific webpage containing a sequence of images representing one chapter of a comic/manga. Represents a single Job in the system.

- **CBZ Format**: Comic Book Archive (essentially a renamed .zip file) containing a sequence of images. The standard output format for Manga Chapters.
- **Auto-Discovery**: A mechanism to detect the URL of the next chapter either by finding a 'Next' UI button or interpolating URL patterns, outputting suggestions to the Terminal.

- **Generic Image Hunter**: A scraping strategy that simulates user scrolling to trigger lazy-loading, extracting all large <img> tags (e.g. >400px width/height), serving as a universal fallback for typical manga sites.
