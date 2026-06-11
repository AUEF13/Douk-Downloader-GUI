# DucK-Downloader-GUI

<p align="center">
  <b>TikTok / Douyin Data Collection & Download Tool — GUI Edition</b>
</p>

## About

This project is a **PySide6 graphical interface** built on top of [DouK-Downloader](https://github.com/JoeanAmier/TikTokDownloader), designed and published by **Xiaomi MiMo**.

The original [DouK-Downloader](https://github.com/JoeanAmier/TikTokDownloader) provides powerful command-line data collection capabilities. This project wraps its core functionality into an intuitive desktop GUI for a simpler and more friendly experience.

## Features

- 📥 **Work Download** — Batch download Douyin/TikTok works via links
- 👤 **Account Download** — Batch collect account posts, likes, and collections
- 🍪 **Cookie Management** — Paste from clipboard or import from file
- ⚙️ **Settings** — Download path, naming format, proxy, platform toggles
- 🌗 **Dark / Light Mode** — One-click toggle with unified global stylesheet
- 📋 **Live Log** — Terminal-style log panel with filtering

## Quick Start

### Option 1: Installer

Download `DucK-Downloader-GUI-1.0.1-Setup.exe` and run it.

### Option 2: From Source

```bash
# Install dependencies
pip install PySide6 qasync
pip install -r requirements.txt

# Launch GUI
python gui_main.py
```

## Project Structure

```
src/gui_edition/
├── __init__.py        # App entry point
├── main_window.py     # Main window + sidebar navigation
├── theme.py           # Theme manager (dark/light)
├── bridge.py          # Bridge between GUI and core logic
├── pages/
│   ├── home_page.py       # Home
│   ├── download_page.py   # Work Download
│   ├── account_page.py    # Account Download
│   ├── cookie_page.py     # Cookie Management
│   ├── settings_page.py   # Settings
│   └── log_page.py        # Live Log
```

## Credits

- [DouK-Downloader](https://github.com/JoeanAmier/TikTokDownloader) — Core logic
- [Xiaomi MiMo](https://github.com/XiaomiMiMo) — GUI design & release

## License

This project is licensed under GPL-3.0. See [license](license) for details.
