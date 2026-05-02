#!/usr/bin/env python3
"""
ParaphraseIt — System-wide paraphrase tool.
Ctrl+Alt+P (Cmd+Alt+P on Mac) to paraphrase text.
Runs as a system tray app on Windows, macOS, and Linux.
"""

import platform
import time
import threading
import os
import sys
import subprocess

from dotenv import load_dotenv
from pynput import keyboard
from pynput.keyboard import Controller, Key
import pyperclip
from google import genai
from PIL import Image
import pystray


def resource_path(filename):
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def app_data_path():
    if SYSTEM == "Windows":
        return os.path.join(os.environ.get("APPDATA", ""), "ParaphraseIt")
    elif SYSTEM == "Darwin":
        return os.path.expanduser("~/Library/Application Support/ParaphraseIt")
    return os.path.expanduser("~/.config/paraphraseit")


def load_config():
    env_path = resource_path(".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    config_env = os.path.join(app_data_path(), ".env")
    if os.path.exists(config_env):
        load_dotenv(config_env, override=True)


SYSTEM = platform.system()
load_config()

kb = Controller()
processing = False
paused = False
current_keys = set()


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


client = get_client()


def enable_autostart():
    exe_path = sys.executable if not getattr(sys, "_MEIPASS", None) else sys.argv[0]
    exe_path = os.path.abspath(exe_path)

    if SYSTEM == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "ParaphraseIt", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to set autostart: {e}")

    elif SYSTEM == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop = f"""[Desktop Entry]
Name=ParaphraseIt
Comment=System-wide paraphrase tool
Exec={exe_path}
Icon=paraphraseit
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
        with open(os.path.join(autostart_dir, "paraphraseit.desktop"), "w") as f:
            f.write(desktop)

    elif SYSTEM == "Darwin":
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(plist_dir, exist_ok=True)
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.paraphraseit.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        with open(os.path.join(plist_dir, "com.paraphraseit.app.plist"), "w") as f:
            f.write(plist)


def is_ctrl_pressed():
    return Key.ctrl_l in current_keys or Key.ctrl_r in current_keys


def is_cmd_pressed():
    return Key.cmd in current_keys or Key.cmd_l in current_keys or Key.cmd_r in current_keys


def is_alt_pressed():
    return Key.alt_l in current_keys or Key.alt_r in current_keys or Key.alt in current_keys


def hotkey_active():
    if SYSTEM == "Darwin":
        return is_cmd_pressed() and is_alt_pressed() and keyboard.KeyCode.from_char("p") in current_keys
    return is_ctrl_pressed() and is_alt_pressed() and keyboard.KeyCode.from_char("p") in current_keys


def copy_key():
    mod = Key.cmd if SYSTEM == "Darwin" else Key.ctrl
    with kb.pressed(mod):
        kb.tap(keyboard.KeyCode.from_char("c"))


def select_all():
    mod = Key.cmd if SYSTEM == "Darwin" else Key.ctrl
    with kb.pressed(mod):
        kb.tap(keyboard.KeyCode.from_char("a"))


def get_text():
    marker = "\x00"
    pyperclip.copy(marker)
    time.sleep(0.05)

    copy_key()
    time.sleep(0.15)

    try:
        selected = pyperclip.paste()
    except Exception:
        return None, False

    if selected != marker and selected.strip():
        return selected, False

    select_all()
    time.sleep(0.05)
    copy_key()
    time.sleep(0.15)

    try:
        all_text = pyperclip.paste()
    except Exception:
        return None, False

    if all_text != marker and all_text.strip():
        return all_text, True

    return None, False


def paste_text(text):
    pyperclip.copy(text)
    time.sleep(0.05)
    mod = Key.cmd if SYSTEM == "Darwin" else Key.ctrl
    with kb.pressed(mod):
        kb.tap(keyboard.KeyCode.from_char("v"))


def paraphrase(text):
    if not client:
        raise RuntimeError("API key not configured")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Paraphrase the following text. Keep the same meaning, tone, and "
            "approximate length, but use different words and sentence structure. "
            "Return ONLY the paraphrased text, nothing else. No quotes, no "
            "explanations, no prefixes.\n\n"
            f"{text}"
        ),
    )
    return response.text


def handle_hotkey():
    global processing
    if processing or paused:
        return
    processing = True

    try:
        text, was_select_all = get_text()

        if not text or not text.strip():
            return

        result = paraphrase(text.strip())

        if was_select_all:
            select_all()
            time.sleep(0.05)
        paste_text(result)

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        processing = False


def on_press(key):
    current_keys.add(key)
    if hotkey_active():
        threading.Thread(target=handle_hotkey, daemon=True).start()


def on_release(key):
    current_keys.discard(key)


def toggle_pause(icon, item):
    global paused
    paused = not paused
    icon.update_menu()


def on_quit(icon, item):
    icon.stop()
    os._exit(0)


def create_tray():
    icon_path = resource_path(os.path.join("assets", "icon_64.png"))
    image = Image.open(icon_path)

    mod_name = "Cmd" if SYSTEM == "Darwin" else "Ctrl"

    menu = pystray.Menu(
        pystray.MenuItem(f"ParaphraseIt — {mod_name}+Alt+P", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            lambda item: "Resume" if paused else "Pause",
            toggle_pause,
        ),
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon("ParaphraseIt", image, "ParaphraseIt", menu)
    return icon


def main():
    enable_autostart()

    if not client:
        print("ERROR: GEMINI_API_KEY not configured")
        sys.exit(1)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

    tray = create_tray()
    tray.run()


if __name__ == "__main__":
    main()
