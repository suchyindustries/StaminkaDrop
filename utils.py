import json
import os
import keyboard
import sys
from PyQt5.QtWidgets import QMessageBox, QApplication
from screen_capture import ScreenCapture

CONFIG_FILE = "config.json"

def load_keybind():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("keybind", "alt+backspace")
    return "alt+backspace"

def save_keybind(keybind):
    config = {"keybind": keybind}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def show_message_and_capture():
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("Calibration Needed")
    msg_box.setText(
        "This is your first run. Inventory needs calibration.\n"
        "Click OK, then open the game, open your inventory, "
        "and press ALT+BACKSPACE to start calibration.\nAfter calibration, run this program again."
    )
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

    print("Waiting for ALT+BACKSPACE key combination...")
    keyboard.wait('alt+backspace')
    print("ALT+BACKSPACE detected. Select screen region...")

    capture_tool = ScreenCapture()
    sys.exit(app.exec_())
