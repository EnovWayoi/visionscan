import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow

def set_dark_theme(app: QApplication):
    # Dark modern palette
    app.setStyle("Fusion")
    
    # Global stylesheet for a premium look
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1E1E1E;
        }
        QWidget {
            color: #E0E0E0;
            background-color: #1E1E1E;
            font-family: "Segoe UI", "Roboto", sans-serif;
        }
        QToolBar {
            background-color: #2D2D30;
            border-bottom: 1px solid #3E3E42;
            padding: 4px;
        }
        QStatusBar {
            background-color: #007ACC;
            color: white;
            font-weight: bold;
        }
        QLabel {
            background-color: transparent;
        }
        QPushButton {
            background-color: #3E3E42;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px 15px;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #007ACC;
        }
        QPushButton:checked {
            background-color: #007ACC;
            border: 1px solid #005A9E;
        }
        QComboBox, QSpinBox {
            background-color: #3E3E42;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px 5px;
            color: white;
        }
        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 4px;
            background: #3E3E42;
            margin: 2px 0;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #007ACC;
            border: 1px solid #007ACC;
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #333333;
            border-radius: 5px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
    """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VisionScan")
    app.setOrganizationName("VisionScanApp")
    
    set_dark_theme(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
