from datetime import datetime
from pynput import keyboard
from ctypes import wintypes
import win32process
import numpy as np
import threading
import pyautogui
import win32con
import win32gui
import random
import psutil
import ctypes
import time
import mss
import cv2
import os

# Load user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Constants for input types
class InputType:
    INPUT_MOUSE = 0
    INPUT_KEYBOARD = 1
    INPUT_HARDWARE = 2

# Constants for key events
class KeyEvent:
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP       = 0x0002
    KEYEVENTF_UNICODE     = 0x0004
    KEYEVENTF_SCANCODE    = 0x0008

# MapVirtualKey constants
MAPVK_VK_TO_VSC = 0

# Virtual Key Definitions
class KeyDef:
    VK_TAB = 0x09
    VK_MENU = 0x12
    VK_BACKSPACE = 0x08
    VK_SPACE = 0x20
    VK_CONTROL = 0x11
    VK_RETURN = 0x0D  # Enter
    VK_F5 = 0x74
    VK_F6 = 0x75
    VK_F7 = 0x76

    VK_LEFT = 0x25
    VK_UP = 0x26
    VK_RIGHT = 0x27
    VK_DOWN = 0x28

    VK_NUMPAD0 = 0x60
    VK_NUMPAD1 = 0x61
    VK_NUMPAD2 = 0x62
    VK_NUMPAD3 = 0x63
    VK_NUMPAD4 = 0x64
    VK_NUMPAD5 = 0x65
    VK_NUMPAD6 = 0x66
    VK_NUMPAD7 = 0x67
    VK_NUMPAD8 = 0x68
    VK_NUMPAD9 = 0x69

    A_KEY = 0x41
    S_KEY = 0x53
    D_KEY = 0x44
    W_KEY = 0x57

# Fix for ULONG_PTR
wintypes.ULONG_PTR = wintypes.WPARAM

# Input structures
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwargs):
        super(KEYBDINPUT, self).__init__(*args, **kwargs)
        if not self.dwFlags & KeyEvent.KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

# Error handling for SendInput
def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)

# Keyboard control class
class KeyboardCtrl:
    PRESS_SLEEP = 0.01  # Delay between press and release

    @staticmethod
    def press_key(hexKeyCode):
        x = INPUT(type=InputType.INPUT_KEYBOARD,
                  ki=KEYBDINPUT(wVk=hexKeyCode))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    @staticmethod
    def release_key(hexKeyCode):
        x = INPUT(type=InputType.INPUT_KEYBOARD,
                  ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KeyEvent.KEYEVENTF_KEYUP))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    @staticmethod
    def press_and_release(hexKeyCode):
        KeyboardCtrl.press_key(hexKeyCode)
        time.sleep(KeyboardCtrl.PRESS_SLEEP)
        KeyboardCtrl.release_key(hexKeyCode)
        time.sleep(KeyboardCtrl.PRESS_SLEEP)

# ========== GLOBALS ==========
game_hwnd = None
game_window_box = None

automation_enabled = True
threshold_trigger_default = int(170 * 0.68)
threshold_trigger = threshold_trigger_default

waiting_for_space = False
current_sequence = []

# ========== LOAD IMAGES ==========
btn_dir = 'btn'
debug_dir = 'debug'
os.makedirs(debug_dir, exist_ok=True)

def load_img(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"[ERROR] Cannot load image: {path}")
    return img

spacen_img = load_img(f'{btn_dir}/spacen.png')

buttons_img = {
    '1b': load_img(f'{btn_dir}/1.png'),
    '1r': load_img(f'{btn_dir}/1d.png'),
    '2b': load_img(f'{btn_dir}/2.png'),
    '2r': load_img(f'{btn_dir}/2d.png'),
    '3b': load_img(f'{btn_dir}/3.png'),
    '3r': load_img(f'{btn_dir}/3d.png'),
    '4b': load_img(f'{btn_dir}/4.png'),
    '4r': load_img(f'{btn_dir}/4d.png'),
    '6b': load_img(f'{btn_dir}/6.png'),
    '6r': load_img(f'{btn_dir}/6d.png'),
    '7b': load_img(f'{btn_dir}/7.png'),
    '7r': load_img(f'{btn_dir}/7d.png'),
    '8b': load_img(f'{btn_dir}/8.png'),
    '8r': load_img(f'{btn_dir}/8d.png'),
    '9b': load_img(f'{btn_dir}/9.png'),
    '9r': load_img(f'{btn_dir}/9d.png'),
}

KEY_MAPPING = {
    'space': KeyDef.VK_SPACE,  # Right Control, hoặc sửa thành VK_SPACE nếu bạn thật sự muốn phím Space: 0x20
    'enter': KeyDef.VK_CONTROL,
    'up': KeyDef.VK_UP,
    'down': KeyDef.VK_DOWN,
    'left': KeyDef.VK_LEFT,
    'right': KeyDef.VK_RIGHT,
    '1': 0x23,  # End
    '2': 0x28,  # Down arrow
    '3': 0x22,  # Page Down
    '4': 0x25,  # Left arrow
    '6': 0x27,  # Right arrow
    '7': 0x24,  # Home
    '8': 0x26,  # Up arrow
    '9': 0x21,  # Page Up
}
# ========== FUNCTIONS ==========
def keyboard_listener():
    def on_press(key):
        global automation_enabled, threshold_trigger

        try:
            if key == keyboard.Key.f5:
                automation_enabled = not automation_enabled
                print(f"[TOGGLE] Automation {'enabled' if automation_enabled else 'disabled'}")

            elif key == keyboard.Key.f6:
                threshold_trigger += 1
                print(f"[ADJUST] threshold_trigger increased to {threshold_trigger}")

            elif key == keyboard.Key.f7:
                threshold_trigger = max(0, threshold_trigger - 1)
                print(f"[ADJUST] threshold_trigger decreased to {threshold_trigger}")

            elif key == keyboard.Key.f8:
                threshold_trigger = threshold_trigger_default
                print(f"[RESET] threshold_trigger reset to {threshold_trigger}")

        except Exception as e:
            print(f"[ERROR] Key press handler: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()


def find_game_window():
    possible_names = ["Audition.exe"]
    hwnd_list = []

    def callback(hwnd, _):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            if proc.name() in possible_names:
                rect = win32gui.GetWindowRect(hwnd)
                if rect[2] - rect[0] > 700:
                    hwnd_list.append((hwnd, rect))
        except Exception:
            pass
        return True

    win32gui.EnumWindows(callback, None)
    return hwnd_list[0] if hwnd_list else (None, None)

def activate_window(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        print(f"[INFO] Activated game window: {hwnd}")
    except Exception as e:
        print(f"[ERROR] Cannot focus game window: {e}")

def capture_region(left, top, width, height):
    with mss.mss() as sct:
        return np.array(sct.grab({'top': top, 'left': left, 'width': width, 'height': height}))

def capture_in_window(x, y, width, height):
    if not game_window_box:
        raise ValueError("Window box not initialized.")
    left, top, _, _ = game_window_box
    return capture_region(left + x, top + y, width, height)

def match_button(screenshot, template, threshold=0.85):
    if screenshot is None or template is None:
        return []

    if screenshot.shape[2] == 4:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
    if template.shape[2] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    return list(zip(*loc[::-1]))

def is_foreground(hwnd):
    return win32gui.GetForegroundWindow() == hwnd

def focus_game_window():
    try:
        win32gui.ShowWindow(game_hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(game_hwnd)
        time.sleep(0.05)
    except Exception as e:
        print(f"[ERROR] Cannot re-focus game window: {e}")

def send_key_to_game(key):
    if not is_foreground(game_hwnd):
        focus_game_window()
        time.sleep(0.5)

    vk_code = KEY_MAPPING.get(key)
    if vk_code:
        #print(f"[SEND] Using SendInput: {key} → {hex(vk_code)}")
        KeyboardCtrl.press_and_release(vk_code)
    else:
        print(f"[WARNING] Unknown or unmapped key: {key}")

def send_text_to_game(text):
    if not is_foreground(game_hwnd):
        print("[INFO] Re-focusing game window before sending text...")
        focus_game_window()

    if is_foreground(game_hwnd):
        pyautogui.typewrite(text)
    else:
        print("[WARNING] Game window not focused — skipped text:", text)

def auto_space():
    global game_window_box, threshold_trigger

    space_triggered = False

    while True:
        if not automation_enabled:
            time.sleep(0.1)
            continue
        region = capture_in_window(520, 520, 170, 16)
        matches = match_button(region, spacen_img, threshold=0.8)

        if matches:
            for (x, y) in matches:
                if x >= threshold_trigger:
                    if not space_triggered:
                        #print(f"[SPACE TRIGGER] spacen_img reached x={x} (>= {threshold_trigger})")
                        send_key_to_game('space')
                        space_triggered = True
                    break 
            else:
                space_triggered = False
        else:
            space_triggered = False

        time.sleep(0.001)

def auto_key():
    global current_sequence, waiting_for_space

    while True:
        if not automation_enabled:
            time.sleep(0.1)
            continue

        if waiting_for_space:
            time.sleep(0.001)
            continue

        screenshot = capture_in_window(294, 545, 445, 40)
        found_buttons = []

        for key, tmpl in buttons_img.items():
            pts = match_button(screenshot, tmpl, threshold=0.85)
            for (x, y) in pts:
                short_key = key[0]
                found_buttons.append((x, short_key))

        found_buttons.sort()
        compressed = []
        last_x = -999
        for x, key in found_buttons:
            if abs(x - last_x) > 10:
                compressed.append(key[0])
                last_x = x

        queue_buttons = compressed
        level = len(queue_buttons)
        #print(f"[SEQUENCE] {' '.join(queue_buttons)} | level={level}")

        if level:
            time.sleep(0.05)
            for key in queue_buttons:
                send_key_to_game(key)
                time.sleep(random.uniform(0.01, 0.05))

        time.sleep(0.001)

# ========== MAIN ==========
def main():
    global game_hwnd, game_window_box

    game_hwnd, game_window_box = find_game_window()
    if not game_hwnd:
        print("[ERROR] Game window not found.")
        return

    activate_window(game_hwnd)
    time.sleep(0.5)
    print("[INFO] Found and activated game window. Starting automation...")
    
    threading.Thread(target=auto_key, daemon=True).start()
    threading.Thread(target=auto_space, daemon=True).start()
    keyboard_listener()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Stopped.")

if __name__ == "__main__":
    main()
