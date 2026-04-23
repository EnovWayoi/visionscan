from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class DetectionItem(QWidget):
    def __init__(self, name: str, confidence: float, parent=None):
        super().__init__(parent)
        self.name = name
        self.confidence = confidence
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Header layout (Name + Percentage)
        header_layout = QHBoxLayout()
        name_label = QLabel(self.name.capitalize())
        name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #E0E0E0;")
        
        conf_int = int(self.confidence * 100)
        pct_label = QLabel(f"{conf_int}%")
        pct_label.setStyleSheet("font-size: 12px; color: #A0A0A0;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(pct_label)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(conf_int)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        
        # Color based on confidence
        if conf_int >= 70:
            color = "#4CAF50" # Green
        elif conf_int >= 40:
            color = "#FF9800" # Orange
        else:
            color = "#F44336" # Red
            
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #333333;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.progress)
        
        # Base styling for the item container
        self.setStyleSheet("""
            DetectionItem {
                background-color: #222222;
                border-radius: 6px;
                border: 1px solid #333333;
            }
            DetectionItem:hover {
                border: 1px solid #555555;
            }
        """)

class DetectionList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
    def update_detections(self, detections):
        # Clear current layout
        self.clear()
        
        # Cap at showing top 20 to avoid UI lag on massive crowds
        for det in detections[:20]:
            item = DetectionItem(det["name"], det["confidence"])
            self.layout.addWidget(item)
            
    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
