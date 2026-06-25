# Facebook Downloader Context

Context and domain language for the Facebook Private Group Downloader.

## Language

**Private Group Video**:
A video posted within a closed or private Facebook Group that requires the user's authenticated session to be viewed.
_Avoid_: Members-only video, secret video

**Cookie Authentication**:
The mechanism of extracting existing session cookies from a local web browser to authenticate requests to Facebook.
_Avoid_: Login, Username/Password authentication

**Flipbook PDF**:
The final output format of a downloaded HTML5 or AnyFlip document. The script should scrape the individual images and compile them into a single PDF artifact.
_Avoid_: Folder of images, E-book zip

**Downloader Plugin**:
An isolated script (like `fb_downloader.py` or `flipbook_downloader.py`) that takes a URL as input and outputs a single media file. The main Flask app routes requests to the correct plugin based on the URL domain.
_Avoid_: Monolith downloader, hardcoded logic
