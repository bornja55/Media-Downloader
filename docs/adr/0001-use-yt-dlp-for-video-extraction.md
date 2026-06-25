# Use yt-dlp for video extraction

We decided to use `yt-dlp` as the core downloading engine instead of building a custom web scraper. Facebook heavily obfuscates its video URLs, splits videos into chunks, and employs aggressive anti-bot mechanisms. `yt-dlp` has robust built-in extractors for Facebook, actively maintained by the community, and supports extracting cookies directly from the local browser. Building a custom scraper would be highly brittle and require constant maintenance.
