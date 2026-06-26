*Read this in other languages: [🇹🇭 ภาษาไทย](README.md), [🇬🇧 English](README_EN.md)*

# 🚀 MEDIA CORE DL: The Ultimate Universal Downloader & Flipbook Extractor

![App Preview](https://img.shields.io/badge/UI-TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![Backend](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)

A premium all-in-one web application (Web GUI) for downloading all types of media, including videos, audio, or access-restricted Flipbooks. Equipped with a smart system that seamlessly bypasses member-only restrictions!

---

## 🔥 Key Features

### 🎥 1. Universal Media Engine
Download videos and audio in the highest available quality (High-Quality Extraction). Supports hundreds of websites and platforms globally, including streaming platforms, social media, and specialized video sites.

### 📚 2. Elite Flipbook Extractor
Break the limits of e-book websites! Extract locked pages from **FlipHTML5** and **AnyFlip**, automatically compiling them into high-resolution PDFs (100% automated). Files are automatically named after the real book title.

### 🔑 3. Smart Authentication (VIP / Member-Only Bypass)
No more screen recording! With **Cookie Extraction** technology, the system securely borrows session data from your local browser (supports Chrome, Edge, Firefox, Brave, Safari, Opera). 
This allows you to extract videos directly from **Facebook Private Groups**, **Member-Only clips**, or **online courses** you already have access to, just as if you were clicking download yourself!

### ⚙️ 4. Settings Dashboard & Top Bar
Control everything from the top-right menu of the application:
- **Dark / Light Mode:** Instantly switch between a cool dark mode and a clean light mode using the ☀️/🌙 icon on the top bar.
- **Settings Window (⚙️):**
  - **Smart Output Directory:** Click the browse folder icon (🔍) to select the destination folder directly via Windows Explorer.
- **One-Click Maintenance:** Buttons to clear operation logs and temporary cookie files for maximum security and privacy.
- **Netscape Cookie Support:** Manually input custom Netscape cookies on the main page, designed for developers or pro users.

### ⚡ 5. Real-Time Batch Processing UI
- Paste hundreds of links; the system will handle downloading sequentially (Batch Processing).
- Futuristic simulated terminal (Hacker-style GUI) that reports real-time status, download percentages, and speed per second.
- Supports custom file naming via templates (e.g., `media_export_%(title)s`).

---

## 💿 Standalone Executable (Portable)

Our program is available as a ready-to-use `.exe` file (One-Click) without needing to install Python. It is divided into 2 main versions:

### 1. `MediaCoreDL-Full.exe` (Recommended)
- **File Size:** ~100MB+
- **Key Feature:** The most complete experience, featuring embedded `ffmpeg`.
- **Advantage:** When downloading high-resolution videos from YouTube (1080p, 4K), the system seamlessly merges the separate high-res video and audio tracks, removing quality limits.

### 2. `MediaCoreDL-Lite.exe` (Space-Saver)
- **File Size:** ~35MB
- **Key Feature:** Fast startup, small size, highly portable.
- **Limitation (if ffmpeg is absent):** If used to download YouTube videos at 1080p or higher, YouTube separates the video and audio tracks. Since the Lite version lacks built-in `ffmpeg`, it cannot merge them. It will fallback to the highest quality pre-merged file available (which YouTube usually caps at **720p**).

> 💡 **For Lite users wanting 1080p+:**
> You can easily install `ffmpeg` yourself:
> 1. Go to [FFmpeg Builds (by BtbN)](https://github.com/BtbN/FFmpeg-Builds/releases) 
> 2. Download the `ffmpeg-master-latest-win64-gpl.zip` file
> 3. Extract the zip and open the `bin` folder
> 4. Copy `ffmpeg.exe` and place it in the same folder as `MediaCoreDL-Lite.exe`
> The program will automatically detect it and resume downloading at 1080p+!

---

## 🛠 Prerequisites

- **Python 3.12+**
- **Google Chrome** (required for the PDF Flipbook extraction system)
- *(Optional)* Other web browsers if you wish to use the cookie extraction feature for restricted files.

---

## 📦 Installation

1. **Clone the Repository:**
   ```bash
   git clone <your-repo-url>
   cd "FB DL"
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 Quick Start

1. **Start the Backend Server:**
   Run the main script via Command Prompt or PowerShell:
   ```bash
   python "FB DL.py"
   ```
2. **Access the Dashboard:**
   Open your web browser and navigate to:
   👉 `http://127.0.0.1:5000`

3. **Configure Settings (Before Downloading):**
   - Click the **Gear icon ⚙️** (top right)
   - Click the search folder icon 🔍 to set your save destination.
   - Toggle **Light Mode ☀️** or **Dark Mode 🌙** to your preference.

4. **Start Downloading:**
   - Select the mode from the top tab: **Video**, **Sound**, or **PDF**
   - Paste the target links into the box (supports multiple lines).
   - **Using Custom Cookies (Required for Member-Only / Private Group clips!):** 
     To download login-restricted content, install the **[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)** extension on Chrome/Edge.
     
     **🚨 VERY IMPORTANT:** You must **first open and keep the video tab (YouTube, Facebook, etc.) running normally**, then click the Extension icon to copy the raw cookie data (Netscape format).
     
     Paste this directly into the **"Custom Cookies"** box in the program (The system relies on this box, 100% success rate!)
     
     <div align="center">
       <img src="assets/extension_guide.png" width="400" alt="How to use Get cookies.txt LOCALLY Extension">
     </div>
   - Click the **Download Queue** button and grab a coffee! ☕

---

## ⚠️ Security & Privacy (Limitations)

- **100% Local Execution:** This program runs entirely on your machine. Passwords and cookies are never sent to external servers. Session cookies are read "temporarily" only when file extraction is required.
- **Headless Chrome:** The Flipbook extraction system stealthily runs Google Chrome in the background (without disrupting your screen). Please do not forcefully close the Chrome process via Task Manager while the system is running.
- **Google Chrome Limitations (App-Bound Encryption):** Due to Google Chrome security updates, automatic cookie extraction may fail (Error #7271). If this happens, please use the **Copy Custom Cookies** method via the extension as detailed in the guide above.

---

## 🤝 Credits & Special Thanks

This project is powered by amazing Open-Source technologies and libraries. Special thanks to:
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** The core engine powering the universal video and audio downloader.
- **[AnyFlip Downloader (by Lofter1)](https://github.com/Lofter1/anyflip-downloader):** The foundational code and concept for extracting images and merging them into PDFs from Flipbook sites, which was further developed and optimized in this project.
