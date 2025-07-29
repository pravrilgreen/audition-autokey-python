
# 🎮 Audition VTC AutoKey Bot (Python + OpenCV)

A Python-based automation tool for **Audition VTC**, using **OpenCV** to detect on-screen note buttons and simulate key presses via Windows API.

> ⏱️ Perfect-timing automation.  
> 🧠 Image-based input detection.  
> 🔁 Real-time control with hotkeys.

---
## 🎥 Demo

![AutoKey Demo](demo.gif)

---

## 🚀 Features

- 🎯 Detects dance/gameplay buttons with OpenCV template matching
- 🧠 Simulates key presses with accurate timing using Windows SendInput
- 🔁 "Perfect" spacebar trigger automation
- 🎛️ Toggle automation or fine-tune detection with hotkeys
- ⚡ Lightweight, low latency — designed for real-time gameplay

---

## ⌨️ Hotkeys

| Key    | Action                                 |
|--------|----------------------------------------|
| `F5`   | Toggle auto-key and auto-space (on/off)|
| `F6`   | Increase `Perfect` space threshold     |
| `F7`   | Decrease `Perfect` space threshold     |
| `F8`   | Reset space threshold to default       |

---

## 🗂️ Folder Structure

```
audition-autokey-python/
│
├── btn/                  # Required: button templates
│   ├── 1.png
│   ├── 1d.png
│   ├── spacen.png
│   └── ... (other buttons)
│
├── debug/                # Optional: for logs/screenshots
├── README.md
├── demo.gif
├── main.py               # Main script
└── requirements.txt      # Python dependencies
```

---

## ⚙️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/pravrilgreen/audition-autokey-python.git
   cd audition-autokey-python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

---

## 🖼️ Button Image Setup

Place your button templates in the `btn/` directory.  
Recommended format:
- `1.png`, `1d.png` → normal and pressed state
- `spacen.png` → image used to trigger space key

Make sure templates match your in-game resolution and theme.

---

## ✅ Requirements

- Windows OS (required for `pywin32` and `SendInput`)
- Python 3.8+
- Installed dependencies:

```
opencv-python
numpy
pyautogui
mss
pynput
psutil
pywin32
```

Install via:
```bash
pip install -r requirements.txt
```

---

## ❗ Notes

- Designed specifically for **Audition VTC** (Vietnam)
- Requires the game window to be open and visible
- May need admin privileges for keyboard control

---

## 📝 License

This project is open-source under the [MIT License](LICENSE).

---

## 🙌 Credits

Created by [@pravrilgreen](https://github.com/pravrilgreen)  
Feel free to star ⭐, fork 🍴, or contribute!
