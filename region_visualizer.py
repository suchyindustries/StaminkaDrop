import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRect

REGION_FILE_FULL = "regions_full.json"
REGION_FILE_SMALL = "regions_small.json"

class RegionVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.regions_full = []
        self.regions_small = []
        self.load_regions()
        self.initUI()

    def load_regions(self):
        try:
            with open(REGION_FILE_FULL, "r") as f:
                self.regions_full = json.load(f)
        except Exception as e:
            print(f"Error loading {REGION_FILE_FULL}: {e}")

        try:
            with open(REGION_FILE_SMALL, "r") as f:
                self.regions_small = json.load(f)
        except Exception as e:
            print(f"Error loading {REGION_FILE_SMALL}: {e}")

    def initUI(self):
        self.setWindowTitle('Region Visualizer')
        self.setWindowOpacity(0.4)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        # Draw regions_full
        pen_full = QPen(QColor(0, 255, 0), 2)  # Green rectangles
        painter.setPen(pen_full)
        for region in self.regions_full:
            rect = QRect(region['x1'], region['y1'], region['x2'] - region['x1'], region['y2'] - region['y1'])
            painter.drawRect(rect)
            painter.drawText(rect, Qt.AlignCenter, region['name'])

        # Draw regions_small
        pen_small = QPen(QColor(255, 0, 0), 2)  # Red rectangles
        painter.setPen(pen_small)
        for region in self.regions_small:
            rect = QRect(region['x1'], region['y1'], region['x2'] - region['x1'], region['y2'] - region['y1'])
            painter.drawRect(rect)

        # Instructions
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignHCenter, "Press ESC to close")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    visualizer = RegionVisualizer()
    sys.exit(app.exec_())
