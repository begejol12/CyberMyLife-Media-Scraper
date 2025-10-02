# CyberMyLife Media Scraper

PyQt6 desktop application dedicated to extracting and downloading images from a target URL. The interface is straightforward, includes a progress indicator, and provides quick links (contact, donation) without leaving the desktop window.

## Features
- **Modern interface**: built with PyQt6 and smooth animations.
- **Fast extraction**: parses `<img>` tags and downloads images concurrently. Future updates will expand the types of assets that can be scraped.
- **Clear monitoring**: progress bar, list of downloaded files, and failure counter.
- **Automatic organization**: every session creates a dedicated `scrap/scrappingX` folder.
- **Bundled HTML pages**: quick access to `donate.html` and `contact.html` keeps the desktop UI uncluttered.

## Requirements
- **Operating system**: Windows 10/11 (currently supported platform).
- **Python**: version 3.10 or higher.
- **Tools**: `git` and `pip`.

## Clone the repository
```powershell
git clone https://github.com/cybermylife/CyberMyLife-Media-Scraper.git
cd CyberMyLife-Media-Scraper
```

## Install dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### `requirements.txt` contains
- PyQt6
- requests
- beautifulsoup4

## Run the application
```powershell
py main.py
```
The window `CyberMyLife - Extract media` opens. Enter the target URL, start the extraction, and the images will be saved in `scrap/`.

## Configuration
Network behaviour is defined in `config.json`:
- `timeout`: maximum duration in seconds for each HTTP request (adjust as needed).
- `max_concurrent_downloads`: maximum number of parallel downloads handled by `ThreadPoolExecutor` (adjust as needed).

## Project structure
```
CyberMyLife-Media-Scraper/
├─ config.json
├─ main.py
├─ interface.py
├─ scraper.py
├─ requirements.txt
├─ src/
│  ├─ contact.html
│  ├─ donate.html
│  └─ icon/favicon.ico
└─ scrap/
```

## Compatibility
- **Windows**: fully supported.
- **macOS/Linux**: not tested. PyQt6 is cross-platform, but Windows-specific behaviour (taskbar icon) will need adjustments.

## Troubleshooting
- **Taskbar icon missing**: ensure `src/icon/favicon.ico` exists and relaunch `py main.py` after closing the app.
- **Module not found (PyQt6, requests, etc.)**: confirm the virtual environment is active and rerun `pip install -r requirements.txt`.
- **No files downloaded**: the URL must expose `<img>` tags with accessible sources. Test in a browser, verify your network, and tweak `timeout` if required.

## Contributing
- Fork the repository and create a feature branch.
- Follow the existing style in `interface.py` and `scraper.py`.
- Suggest improvements such as cross-platform support, advanced filtering, logging, and more.

## License
- MIT License
