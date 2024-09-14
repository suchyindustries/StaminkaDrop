import json
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPainter, QColor
import os

REGION_FILE_FULL = "regions_full.json"
REGION_FILE_SMALL = "regions_small.json"

class ScreenCapture(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Screen Capture')
        self.setWindowOpacity(0.6)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(0, 0, 0))
        painter.drawRect(self.rect())

        instructions = (
            "Click and drag to select your inventory region.\n"
            "Release the mouse to finalize the selection."
        )
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, instructions)

        if self.start_pos and self.end_pos:
            painter.setBrush(QColor(255, 255, 255, 50))
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)
            self.draw_grid_lines(painter, rect)

    def draw_grid_lines(self, painter, rect):
        col_width = rect.width() / 11
        row_height = rect.height() / 3

        for i in range(1, 11):
            x = int(rect.left() + i * col_width)
            painter.drawLine(x, rect.top(), x, rect.bottom())

        for j in range(1, 3):
            y = int(rect.top() + j * row_height)
            painter.drawLine(rect.left(), y, rect.right(), y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_pos = event.pos()
            self.close()
            selected_region = QRect(self.start_pos, self.end_pos).normalized()
            print(f"Selected Region Coordinates: {selected_region.getCoords()}")
            self.calculate_regions(selected_region)
            self.capture_screenshot(selected_region)

    def calculate_regions(self, selected_region):
        col_width = selected_region.width() / 11
        row_height = selected_region.height() / 3

        regions_full = []
        regions_small = []


        for row in range(3):
            for col in range(11):
                x1 = selected_region.left() + col * col_width
                y1 = selected_region.top() + row * row_height
                x2 = x1 + col_width
                y2 = y1 + row_height

                # Calculate 2% smaller region
                shrink_factor = 0.02
                x1_shrunk = int(x1 + col_width * shrink_factor)
                y1_shrunk = int(y1 + row_height * shrink_factor)
                x2_shrunk = int(x2 - col_width * shrink_factor)
                y2_shrunk = int(y2 - row_height * shrink_factor)

                regions_full.append({
                    "name": chr(ord('a') + row) + str(col + 1),
                    "x1": x1_shrunk,  # Use shrunk coordinates
                    "y1": y1_shrunk,
                    "x2": x2_shrunk,
                    "y2": y2_shrunk
                })

                small_width = col_width * 0.15
                small_height = row_height * 0.70
                small_x1 = x1 + (col_width - small_width) / 4
                small_y1 = y1 + (row_height - small_height) / 4

                regions_small.append({
                    "name": chr(ord('a') + row) + str(col + 1),
                    "x1": int(small_x1),
                    "y1": int(small_y1),
                    "x2": int(small_x1 + small_width),
                    "y2": int(small_y1 + small_height)
                })

        self.save_regions(REGION_FILE_FULL, regions_full)
        self.save_regions(REGION_FILE_SMALL, regions_small)
        print(f"Regions saved to {REGION_FILE_FULL} and {REGION_FILE_SMALL}")

    @staticmethod
    def save_regions(filename, regions):
        with open(filename, "w") as f:
            json.dump(regions, f, indent=4)

    def capture_screenshot(self, selected_region):
        screen = QApplication.primaryScreen()
        if not screen:
            print("Error: No screen found!")
            return

        capture_width = selected_region.width() * (2.5 / 11)
        capture_height = selected_region.height() * (2.5 / 11)
        capture_x = selected_region.right() - capture_width
        capture_y = selected_region.top() - capture_height

        capture_region = QRect(int(capture_x), int(capture_y), int(capture_width), int(capture_height))
        screenshot = screen.grabWindow(0, capture_region.x(), capture_region.y(), capture_region.width(), capture_region.height())
        screenshot_file = "inv.png"
        screenshot.save(screenshot_file, "png")
        print(f"Screenshot saved as {screenshot_file}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen_capture = ScreenCapture()
    sys.exit(app.exec_())
