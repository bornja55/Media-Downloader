Status: ready-for-agent

## Problem Statement

Users of the Universal Media Downloader currently have the ability to download Videos, Sounds, and PDF Flipbooks. However, they lack the ability to download Manga/Webtoon chapters from comic reading websites. Since manga sites often use protections like Lazy Loading, require logins for premium chapters, and the user wants to read them offline in standard comic reader formats, they need a dedicated tool within the app to handle this cleanly.

## Solution

A new "Manga" mode in the application that acts as a Generic Image Hunter. It will simulate a user browsing a manga chapter, scrolling down to defeat lazy loading, extracting all significant high-resolution images, and compiling them into a single `.cbz` (Comic Book Zip) file. It will also leverage the existing Cookie Bypass system to access locked/paid chapters. Furthermore, it will attempt to Auto-Discover the URL of the next chapter and suggest it to the user.

## User Stories

1. As a user, I want to see a "Manga" tab in the web UI, so that I can select it when downloading from a comic website.
2. As a user, I want to paste a link to a Manga Chapter, so that the app can queue it for download.
3. As a user reading paid content, I want to supply my custom cookies (or select my browser), so that the app can bypass the paywall and see the locked images.
4. As a user downloading from a lazy-loaded website, I want the bot to automatically scroll the page, so that all images are triggered to load before extraction.
5. As a user who dislikes cluttered files, I want the output to be a single `.cbz` file named after the chapter, so that I can easily open it in a Comic Reader app.
6. As a user who only wants the manga pages, I want the scraper to filter out small icons and UI elements (e.g. < 400x400px), so that my comic file doesn't contain garbage images.
7. As a user downloading a series, I want the console to print the URL of the "Next Chapter" if it finds one, so that I don't have to manually hunt for the next link on the website.
8. As a user tracking progress, I want to see the real-time status in the terminal GUI, so that I know what the Generic Image Hunter is currently doing (e.g., "Scrolling...", "Extracting images...", "Zipping CBZ...").

## Implementation Decisions

- **MangaDownloader Module:** A new Python class `MangaDownloader` will be built (similar to `PDFDownloader`) using Selenium to navigate and scroll the page.
- **Generic Image Hunter:** The scraper will find all `<img>` tags, retrieve their `src`, download them via `requests` (passing the cookies), filter by dimensions (>400px), and sequence them.
- **CBZ Compilation:** Downloaded images will be placed in a temporary directory, zipped using Python's `zipfile` module, and then the `.zip` will be renamed to `.cbz` in the final Output Directory.
- **Auto-Discovery:** After images are extracted, the scraper will look for `<a>` tags containing typical "Next" keywords (Next, ถัดไป, ตอนต่อไป, >). If found, it prints `[Auto-Discovery] Found next chapter: <URL>` to the terminal log.
- **Frontend Updates:** Add a Manga button to the Tab navigation in `index.html`. Update `FB DL.py`'s `/api/download` route to accept `mode == 'manga'` and route the Job to `MangaDownloader`.

## Testing Decisions

- **Testing Seams:** The primary seam for automated testing (if tests are added) would be the `MangaDownloader.download()` method, passing a mock URL and mocking the Selenium webdriver. For end-to-end verification, the seam is the `/api/download` endpoint.
- **Verification Criteria:** 
  - Submitting a URL of a known lazy-loaded manga site successfully generates a valid `.cbz` file.
  - The `.cbz` file opens correctly in a comic reader.
  - Small UI images are excluded from the archive.
  - Providing a URL with a "Next" button successfully logs the next URL to the console.

## Out of Scope

- Scraping an entire series automatically from a Main Series Page URL (only Single Chapter links are supported for now).
- Site-specific reverse-engineering for websites that heavily obfuscate images using `<canvas>` or custom DRM (the Generic Image Hunter will fail on these by design, and they will be handled case-by-case in the future).

## Further Notes

- The `Manga Chapter`, `CBZ Format`, `Auto-Discovery`, and `Generic Image Hunter` domain concepts have been recorded in `CONTEXT.md`.
