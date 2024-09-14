import sys
import os
from PyQt5.QtWidgets import QApplication
from utils import show_message_and_capture
from config_window import ConfigWindow

REGION_FILE = "regions_small.json"

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ("-f", "-fresh"):
        # Force fresh calibration
        if os.path.exists(REGION_FILE):
            os.remove(REGION_FILE)
        show_message_and_capture()
    elif os.path.exists(REGION_FILE):
        # Show configuration window if regions.json is present
        app = QApplication(sys.argv)
        config_window = ConfigWindow()
        sys.exit(app.exec_())
    else:
        # Show calibration message and capture screen if regions.json is not present
        show_message_and_capture()
