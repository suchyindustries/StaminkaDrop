import json
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QMenu, QAction
)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QKeySequence, QCursor
import keyboard

import staminka_dropall
from region_visualizer import RegionVisualizer  # Import the new visualizer class

CONFIG_FILE = "config.json"
LOCAL_VERSION = "0.0.1"
REMOTE_VERSION_URL = "todo"

def check_version():
    
    pass

def load_config():
    default_config = {
        "keybind": "ctrl+shift+d",
        "inventory_key": "i",
        "threshold": 0.89,
        "menu_keybind": "ctrl+d"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Ensure all keys are present
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except json.JSONDecodeError:
            print("Error decoding JSON config. Using default configuration.")
    return default_config

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
    except IOError as e:
        print(f"An error occurred while saving the config: {e}")

class KeybindButton(QPushButton):
    def __init__(self, label, parent=None):
        super().__init__(label, parent)
        self.listening = False
        self.current_keybind = ""
        self.pressed_keys = []

    def start_listening(self):
        self.setText("Press key combination...")
        self.listening = True
        self.current_keybind = ""
        self.pressed_keys.clear()
        self.setFocus()  # Ensure the button has focus to receive key events

    def set_keybind(self, key_sequence):
        self.current_keybind = key_sequence
        self.setText(f"Keybind: {key_sequence}")
        self.listening = False
        self.pressed_keys.clear()

    def keyPressEvent(self, event):
        if self.listening:
            key_names = self.get_key_names(event)
            if key_names:
                self.pressed_keys = key_names
                key_sequence = "+".join(self.pressed_keys)
                self.setText(f"Press key combination... ({key_sequence})")
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.listening:
            key_sequence = "+".join(self.pressed_keys)
            self.set_keybind(key_sequence)
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def get_key_names(self, event):
        key = event.key()
        modifiers = event.modifiers()

        # Map the modifier keys
        mods = []
        if modifiers & Qt.ControlModifier:
            mods.append('ctrl')
        if modifiers & Qt.AltModifier:
            mods.append('alt')
        if modifiers & Qt.ShiftModifier:
            mods.append('shift')
        if modifiers & Qt.MetaModifier:
            mods.append('cmd')  # For Mac compatibility, if needed

        # Map the key pressed
        key_name = ''
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            # Modifier key alone
            pass  # Already handled in modifiers
        else:
            key_name = QKeySequence(key).toString(QKeySequence.NativeText).lower()
            if not key_name:
                key_name = event.text().lower()
            if not key_name:
                # As a last resort, map the key code to a name
                key_name = self.map_key_code_to_name(key)
            if key_name:
                key_name = key_name.strip()

        # Combine modifiers and key
        if key_name:
            return mods + [key_name]
        else:
            return mods

    def map_key_code_to_name(self, key_code):
        # Add any additional key code mappings as needed
        key_map = {
            Qt.Key_Escape: 'esc',
            Qt.Key_Tab: 'tab',
            Qt.Key_Backspace: 'backspace',
            Qt.Key_Return: 'enter',
            Qt.Key_Enter: 'enter',
            Qt.Key_Insert: 'insert',
            Qt.Key_Delete: 'delete',
            Qt.Key_Pause: 'pause',
            Qt.Key_Print: 'print_screen',
            Qt.Key_Space: 'space',
            Qt.Key_Home: 'home',
            Qt.Key_End: 'end',
            Qt.Key_Left: 'left',
            Qt.Key_Up: 'up',
            Qt.Key_Right: 'right',
            Qt.Key_Down: 'down',
            Qt.Key_PageUp: 'page_up',
            Qt.Key_PageDown: 'page_down',
            Qt.Key_CapsLock: 'caps_lock',
            Qt.Key_NumLock: 'num_lock',
            Qt.Key_ScrollLock: 'scroll_lock',
            # Add function keys
            Qt.Key_F1: 'f1',
            Qt.Key_F2: 'f2',
            Qt.Key_F3: 'f3',
            Qt.Key_F4: 'f4',
            Qt.Key_F5: 'f5',
            Qt.Key_F6: 'f6',
            Qt.Key_F7: 'f7',
            Qt.Key_F8: 'f8',
            Qt.Key_F9: 'f9',
            Qt.Key_F10: 'f10',
            Qt.Key_F11: 'f11',
            Qt.Key_F12: 'f12',
            # Add more keys as needed
        }
        return key_map.get(key_code, '')

class ConfigWindow(QWidget):
    show_menu_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dragging = False
        self.offset = None
        self.hotkeys_registered = {}  # Dictionary to manage multiple hotkeys
        self.config_data = load_config()
        self.initUI()
        self.show_menu_signal.connect(self.show_menu_main_thread)  # Connect the signal

    def initUI(self):
        self.setWindowTitle("StaminkaDrop")
        self.setGeometry(100, 100, 300, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(self.get_stylesheet())

        layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        exit_button = QPushButton("X")
        exit_button.clicked.connect(self.exit_program)
        top_layout.addWidget(exit_button, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)

        # Drop keybind
        layout.addWidget(QLabel("Drop keybind:"))
        self.keybind_button = KeybindButton("Set Keybind")
        self.keybind_button.clicked.connect(self.keybind_button.start_listening)
        layout.addWidget(self.keybind_button)

        # Inventory keybind
        layout.addWidget(QLabel("Inventory keybind:"))
        self.inventory_keybind_button = KeybindButton("Set Inventory Keybind")
        self.inventory_keybind_button.clicked.connect(self.inventory_keybind_button.start_listening)
        layout.addWidget(self.inventory_keybind_button)

        # Menu keybind
        layout.addWidget(QLabel("Menu keybind:"))
        self.menu_keybind_button = KeybindButton("Set Menu Keybind")
        self.menu_keybind_button.clicked.connect(self.menu_keybind_button.start_listening)
        layout.addWidget(self.menu_keybind_button)

        # Threshold slider
        layout.addWidget(QLabel("Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(1, 100)
        self.threshold_slider.setValue(int(self.config_data["threshold"] * 100))
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        layout.addWidget(self.threshold_slider)

        self.current_threshold_label = QLabel(f"Current Threshold: {self.config_data['threshold']:.2f}")
        layout.addWidget(self.current_threshold_label)

        # Show Regions button
        self.show_regions_button = QPushButton("Show Regions")
        self.show_regions_button.clicked.connect(self.show_regions)
        layout.addWidget(self.show_regions_button)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_program)
        layout.addWidget(self.start_button)

        remote_version = check_version()
        version_text = (
            f"Version: {LOCAL_VERSION}" if not remote_version
            else f"Out of date ({LOCAL_VERSION}), please update to {remote_version}"
        )
        version_label = QLabel(version_text)
        version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(version_label)

        self.setLayout(layout)
        self.load_initial_config()
        self.show()

    def load_initial_config(self):
        self.keybind_button.set_keybind(self.config_data["keybind"])
        self.inventory_keybind_button.set_keybind(self.config_data["inventory_key"])
        self.menu_keybind_button.set_keybind(self.config_data["menu_keybind"])

    def update_threshold(self, value):
        self.config_data["threshold"] = value / 100.0
        self.current_threshold_label.setText(f"Current Threshold: {self.config_data['threshold']:.2f}")

    def start_program(self):
        self.config_data["keybind"] = self.keybind_button.current_keybind
        self.config_data["inventory_key"] = self.inventory_keybind_button.current_keybind
        self.config_data["menu_keybind"] = self.menu_keybind_button.current_keybind
        save_config(self.config_data)

        if not self.hotkeys_registered:
            self.keybind_button.setEnabled(False)
            self.inventory_keybind_button.setEnabled(False)
            self.menu_keybind_button.setEnabled(False)
            self.start_button.setText("Stop")
            # Register hotkeys
            self.hotkeys_registered["dropall"] = keyboard.add_hotkey(
                self.config_data["keybind"], self.run_staminka_dropall
            )
            self.hotkeys_registered["menu"] = keyboard.add_hotkey(
                self.config_data["menu_keybind"], self.show_menu
            )
        else:
            self.stop_program()

    def stop_program(self):
        if self.hotkeys_registered:
            for hotkey in self.hotkeys_registered.values():
                keyboard.remove_hotkey(hotkey)
            self.hotkeys_registered = {}
        self.keybind_button.setEnabled(True)
        self.inventory_keybind_button.setEnabled(True)
        self.menu_keybind_button.setEnabled(True)
        self.start_button.setText("Start")

    def run_staminka_dropall(self):
        print("Keybind activated, running staminka_dropall.main('dropall')")
        staminka_dropall.main(action="dropall")

    def show_menu(self):
        # Emit the signal to show the menu in the main thread
        self.show_menu_signal.emit()

    def show_menu_main_thread(self):
        print("Menu keybind activated, showing menu")
        # Get mouse cursor position
        cursor_pos = QCursor.pos()
        # Adjust position to the left of the cursor
        menu_pos = cursor_pos - QPoint(150, 0)  # Adjust the value as needed

        # Create the menu
        self.menu = QMenu()

        action_dropall = QAction("Drop All", self)
        action_dropall.triggered.connect(lambda: staminka_dropall.main(action="dropall"))
        self.menu.addAction(action_dropall)

        action_dropallexceptga = QAction("Drop All Except GA", self)
        action_dropallexceptga.triggered.connect(lambda: staminka_dropall.main(action="dropallexceptga"))
        self.menu.addAction(action_dropallexceptga)

        action_dropgaonly = QAction("Drop GA Only", self)
        action_dropgaonly.triggered.connect(lambda: staminka_dropall.main(action="dropgaonly"))
        self.menu.addAction(action_dropgaonly)

        # Show the menu at the adjusted position
        self.menu.exec_(menu_pos)

    def show_regions(self):
        # Create an instance of RegionVisualizer
        self.region_visualizer = RegionVisualizer()
        self.region_visualizer.show()

    def exit_program(self):
        self.stop_program()
        QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None

    @staticmethod
    def get_stylesheet():
        return """
            QWidget { background-color: #2E2E2E; color: #FFFFFF; }
            QPushButton { background-color: #3B3B3B; color: #FFFFFF; border: 1px solid #4A4A4A; padding: 5px; }
            QPushButton:hover { background-color: #4A4A4A; }
            QPushButton:disabled { background-color: #555555; color: #888888; border: 1px solid #666666; }
            QLabel { font-size: 14px; }
            .version { font-size: 10px; color: #AAAAAA; margin-top: 10px; }
        """

if __name__ == "__main__":
    app = QApplication([])
    window = ConfigWindow()
    app.exec_()
