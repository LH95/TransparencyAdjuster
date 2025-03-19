import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter
import win32gui
import win32con
import win32api

class CustomSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paw = QPixmap(resource_path("paw.png"))
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                background: transparent;
                width: 20px;
                margin: -10px 0;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        handle_position = self.style().sliderPositionFromValue(self.minimum(), self.maximum(),
                                                               self.value(), self.width() - self.paw.width())
        painter.drawPixmap(handle_position, 0, self.paw)

class TransparencyTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我在認真上班")
        self.selected_hwnds = []
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title input
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("輸入視窗標題或選擇:"))
        self.title_input = QLineEdit("新分頁")
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Buttons
        button_layout = QHBoxLayout()
        buttons = [
            ("新分頁", lambda: self.set_default_title(1)),
            ("新無痕分頁", lambda: self.set_default_title(2)),
            ("記事本", lambda: self.set_default_title(4)),
            ("LINE", lambda: self.set_default_title(5))
        ]
        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            button_layout.addWidget(button)
        layout.addLayout(button_layout)

        button_layout2 = QHBoxLayout()
        buttons2 = [
            ("Word", lambda: self.set_default_title(6)),
            ("Excel", lambda: self.set_default_title(7)),
            ("PowerPoint", lambda: self.set_default_title(8)),
            ("VS Code", lambda: self.set_default_title(3))
        ]
        for text, callback in buttons2:
            button = QPushButton(text)
            button.clicked.connect(callback)
            button_layout2.addWidget(button)
        layout.addLayout(button_layout2)

        # Transparency slider
        transparency_layout = QHBoxLayout()
        transparency_layout.addWidget(QLabel("設置透明度:"))
        self.transparency_label = QLabel("50")
        transparency_layout.addWidget(self.transparency_label)
        self.transparency_slider = CustomSlider(Qt.Horizontal)
        self.transparency_slider.setRange(0, 255)
        self.transparency_slider.setValue(50)
        self.transparency_slider.valueChanged.connect(self.set_transparency)
        transparency_layout.addWidget(self.transparency_slider)
        layout.addLayout(transparency_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

    def set_window_transparency(self, hwnd, transparency):
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style |= win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), transparency, win32con.LWA_ALPHA)

    def find_window_by_title(self, title):
        def callback(hwnd, extra):
            if title.lower() in win32gui.GetWindowText(hwnd).lower():
                extra.append(hwnd)
        hwnd_list = []
        win32gui.EnumWindows(callback, hwnd_list)
        return hwnd_list

    def set_transparency(self, transparency):
        self.find_windows()
        if self.selected_hwnds:
            for hwnd in self.selected_hwnds:
                self.set_window_transparency(hwnd, transparency)
        else:
            self.status_label.setText(f"找不到標題包含 '{self.title_input.text()}' 的視窗")
            QTimer.singleShot(5000, self.clear_status)
        
        self.transparency_label.setText(str(transparency))

    def find_windows(self):
        title = self.title_input.text()
        if title == "":
            self.status_label.setText("請輸入視窗標題")
            QTimer.singleShot(5000, self.clear_status)
            return
        self.selected_hwnds = self.find_window_by_title(title)
        if not self.selected_hwnds:
            self.status_label.setText(f"找不到標題包含 '{title}' 的視窗")
            QTimer.singleShot(5000, self.clear_status)

    def set_default_title(self, option):
        titles = {
            1: "新分頁", 2: "新無痕分頁", 3: "Visual Studio Code",
            4: "記事本", 5: "LINE", 6: "Word", 7: "Excel", 8: "PowerPoint"
        }
        self.title_input.setText(titles.get(option, ""))
        self.find_windows()

    def clear_status(self):
        self.status_label.setText("")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TransparencyTool()
    ex.show()
    sys.exit(app.exec_())