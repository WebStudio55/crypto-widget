# crypto-widget
A sleek cryptocurrency price widget for Windows 10/11. Displays live prices with rotating coin slides, customizable UI, draggable transparent window, and always-on-top support. Built with Python + PyQt6.
Overview

Crypto Price Widget is a modern desktop widget for Windows 10/11 that displays real-time cryptocurrency prices using the Binance API.
It runs as a small, transparent, movable window that stays on top of all applications — even above the taskbar.

Perfect for traders, developers, and anyone who wants live crypto prices visible at all times.

✨ Features

✔ Live Binance Price Feed (auto refresh)

✔ Three-symbol rotating slide transitions

✔ Smooth animated sliding UI

✔ Customizable symbols & decimal places

✔ Font size & background opacity controls

✔ Always on top (even above taskbar)

✔ Draggable + resizable frameless design

✔ Startup option for Windows

✔ Local icon caching for fast load

✔ Right-click settings menu

✔ No console window (clean EXE)

✔ Lightweight & low-CPU usage

🖼️ Screenshots


📦 Installation
Option 1 — Download EXE (recommended)

Download the latest release from:

👉 Releases → crypto-widget.exe

No installation needed. Just run the file.

Option 2 — Add to Windows Startup

The widget automatically supports startup.
To enable:

Open Settings from right-click menu

Enable Start With Windows (if available)

Or manually place shortcut in:

%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

⚙️ Configuration Options

Inside Settings, you can change:

Coin symbols (BTCUSDT, ETHUSDT, SOLUSDT, etc.)

Decimal precision for each coin

Update frequency for price refresh

Slide animation interval

Font size (8–64px)

Background transparency (0–100%)

Enable/disable automatic symbol rotation

Widget position is saved automatically

Settings file is stored at:

C:\Users\<username>\crypto_widget_settings.json

🛠️ Build From Source
1. Install Python Dependencies
pip install PyQt6 requests

2. Run the app
python crypto-widget.py

3. Build Windows EXE
pyinstaller --noconsole --onefile --windowed --icon=cw.ico crypto-widget.py


The EXE will appear in:

/dist/crypto-widget.exe

📁 Project Structure
├── crypto-widget.py        # Main source code
├── cw.ico                  # Application icon
├── crypto_widget_settings.json  # Auto-created settings file
├── /screenshots/           # Images for README
└── /dist/                  # Built application

🌐 API

Real-time price data is fetched from:
👉 https://api.binance.com/api/v3/ticker/price

Only public endpoints are used — no API key required.

🧩 Technologies Used

Python 3.12

PyQt6

Requests (Binance price fetching)

PyInstaller (packaging to .exe)

Windows API (ctypes) for override taskbar behavior

📝 License

This project is licensed under the MIT License.
Feel free to use, modify, and distribute.

⭐ Support the Project

If you find this useful:

⭐ Star the repo

🐞 Report any issues

📢 Share it with others

💬 Contact / Contributions

Pull requests are welcome!
