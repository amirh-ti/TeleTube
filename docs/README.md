<p align="center">
  <img src="../media/logo.svg" width="320" alt="TeleTube Logo">
</p>

<h1 align="center">⚡ TeleTube ⚡</h1>

<p align="center">
  <b>A fast, modern, open-source Telegram bot for downloading YouTube videos without Bot API upload size limits.</b>
</p>

<p align="center">
  <a href="README.fa.md"><b>فارسی</b></a> • 
  <a href="#-project-overview">Features</a> • 
  <a href="#-quick-start">Quick Start</a> • 
  <a href="#%EF%B8%8F-configuration">Configuration</a> • 
  <a href="#-architecture-and-workflow">Architecture</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/Powered%20by-yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="yt-dlp">
  <img src="https://img.shields.io/badge/Linux-Ubuntu%20%7C%20Debian-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" alt="OS">
  <img src="https://img.shields.io/github/license/amirh-ti/TeleTube?style=for-the-badge&color=blue" alt="License">
</p>

---

## 📌 Project Overview

Standard Telegram bots face severe upload size restrictions imposed by the Bot API. **TeleTube** solves this issue by using a hybrid architecture:
- **python-telegram-bot** manages user interactions, inline menus, and commands.
- **Telethon** (a personal client account) uploads videos at high speeds and without size limits to a Telegram channel.
- After uploading, the video is automatically forwarded to the user to provide a fast and unrestricted experience.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🚀 High-Speed Downloading** | Powered by `yt-dlp` along with the `aria2` download accelerator. |
| **🎛️ Smart Quality Menu** | Automatically detects available video qualities and displays an inline menu for selection. |
| **⏱️ Automatic Selection** | Automatically selects the best quality if the user does not respond after 15 seconds. |
| **📦 No Size Limit** | Bypasses Bot API upload limits by using the MTProto protocol (`Telethon`). |
| **📊 Live Progress Reporting** | Displays real percentage progress in both download and upload stages. |
| **⚙️ Automatic Processing** | Merges files with FFmpeg, creates thumbnails, and cleans up temporary files. |
| **🔑 Cookie Support** | Enables downloading age-restricted or limited videos using HTTP cookies. |
| **🛠️ Service Management** | Includes a default Systemd service for running in the background and starting up on server boot. |

---

<details>
<summary>📸 Click to view Screenshots</summary>

<br>

<p align="center">
  <img src="../media/start.jpg" width="280" alt="TeleTube Start Command">
  <img src="../media/select_qualities.jpg" width="280" alt="Video Quality Selection Menu">
</p>

<p align="center">
  <img src="../media/download.jpg" width="280" alt="Video Download Progress">
  <img src="../media/upload.jpg" width="280" alt="Telegram Upload Progress">
</p>

<p align="center">
  <img src="../media/end.jpg" width="280" alt="Completed Video Delivery">
</p>

</details>

---

## 🚀 Quick Start

### Prerequisites
- **Operating System:** Ubuntu 22.04+ / Debian 11+ (`amd64` / `arm64`)
- **Hardware:** Minimum 1 CPU Core, 1 GB RAM, 2 GB Free Space

### Installation
Run the automatic installation script. This script installs all prerequisites (Python, `FFmpeg`, `aria2`, and `Deno`) and configures the systemd service:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/amirh-ti/TeleTube/main/install.sh)
```

### Uninstallation
To completely remove the TeleTube project (including the systemd service and all installed files), run the automatic uninstaller script:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/amirh-ti/TeleTube/main/uninstall.sh)
```

---

## ⚙️ Configuration

Project settings are stored in the `/opt/TeleTube/.env` file:

```bash
nano /opt/TeleTube/.env
```

### Environment Variables

```env
# Telegram authentication info (Mandatory)
TELEGRAM_TOKEN=123456789:AA...
API_ID=12345678
API_HASH=0123456789abcdef0123456789abcdef
SESSION_STRING=1BV...

# Target channel info for uploading
TARGET_CHANNEL=https://t.me/my_channel
TARGET_CHANNEL_USERNAME=@my_channel

# Optional settings
DOWNLOAD_DIR=/root/TeleTube/youtube_memory
COOKIES_FILE=/root/TeleTube/cookies.txt

AUTO_SELECT_TIMEOUT=15
```

---

## 🔑 Prerequisites

To use this project, you need Telegram **API ID** and **API Hash**.

Don't have them? No worries! A complete step-by-step guide for obtaining them is available in the file below:

📘 **[Guide to Getting API ID and API Hash](telegram_api_en.md)**

Make sure to read this file before running the project.

---

> 💡 **Note:** If you don't have a `SESSION_STRING`, you can generate it by running the ready-made script below (after installing TeleTube):
> ```bash
> cd /opt/TeleTube/
> python3 utils/sess_st.py
> ```
## 🛠️ Service Management

Use `systemctl` commands to control and manage the bot in the background:

```bash
# Start the service and enable auto-start on boot
systemctl enable --now TeleTube

# Check service status
systemctl status TeleTube

# View live logs
journalctl -u TeleTube -f

# Restart after changing settings
systemctl restart TeleTube

# Update project to the latest version
TeleTube update
```

---

## 🔄 Architecture and Workflow

```text
               ┌──────────────────────────────┐
               │        Telegram User         │
               └──────────────┬───────────────┘
                              │ Sends Link
                              ▼
               ┌──────────────────────────────┐
               │    python-telegram-bot       │
               │ Quality Menu / UI Interface  │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │        yt-dlp + aria2        │
               │   (High-Speed Multi-Thread)  │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │      FFmpeg + Thumbnail      │
               │   (Video Merge & Thumb Gen)  │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │           Telethon           │
               │    (Upload to Channel via)   │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │    Forward Video to User     │
               └──────────────────────────────┘
```

---

## 📁 Project Structure

```text
TeleTube/
├── bot.py                     # Entry point and main program
├── config.py                  # Environment variable reading module
├── install.sh                 # Linux automatic installation script
├── uninstall.sh               # Complete application removal script
├── .env.example               # Configuration file template
│
├── core/                      # Main core application logic
│   ├── downloader.py          # Download module with yt-dlp and aria2
│   ├── uploader.py            # Upload module with Telethon
│   ├── qualities.py           # Detecting and extracting qualities
│   ├── thumbnail.py           # Generating video thumbnails
│   └── cleanup.py             # Temporary file cleanup
│
├── handlers/                  # Telegram handlers
│   ├── start.py               # /start command
│   ├── message.py             # Receiving links from users
│   └── callback.py            # Clicking inline buttons
│
└── utils/                     # Helper functions, logger, and validation
```

---

## 🗺️ Roadmap

- [ ] **Display estimated file size:** Adding video size next to quality buttons (e.g., `1080p • ~145 MB`).
- [ ] **Playlist support:** Full batch downloading of YouTube playlists.
- [ ] **Support for other platforms:** Adding Instagram, TikTok, and Twitter.
- [ ] **Containerization:** Providing ready `Docker` and `Docker Compose` files.

---

## 🤝 Contribution and Support

Contributions to project development, submitting bug reports, and suggestions are always welcome!

1. **Fork** the project.  
2. Create a new branch (`git checkout -b feature/AmazingFeature`).  
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).  
4. **Push** the branch (`git push origin feature/AmazingFeature`).  
5. Submit a **Pull Request**.  

If the **TeleTube** project was useful to you, please support it by giving a **⭐ Star** on GitHub!

---

## 📜 Acknowledgements

This project was built using the following incredible open-source tools:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [yt-dlp-ejs](https://github.com/yt-dlp/yt-dlp-ejs)
- [FFmpeg](https://ffmpeg.org/) and [aria2](https://aria2.github.io/)
