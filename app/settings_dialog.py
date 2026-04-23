from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QSlider, QPushButton, QCheckBox,
    QGroupBox, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtMultimedia import QMediaDevices

class SettingsDialog(QDialog):
    # Signals emitted when settings change that require immediate updates
    settings_changed = pyqtSignal()
    model_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VisionScan Settings")
        self.setFixedSize(350, 450)
        self.settings = QSettings("VisionScanApp", "Settings")
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Model Settings ---
        model_group = QGroupBox("Model Configuration")
        model_layout = QFormLayout(model_group)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["yolo11n", "yolo11s", "yolo11m", "yolo11l", "yolo11x"])
        model_layout.addRow("YOLOv11 Version:", self.model_combo)
        
        main_layout.addWidget(model_group)
        
        # --- Hardware Settings ---
        hw_group = QGroupBox("Hardware Configuration")
        hw_layout = QFormLayout(hw_group)
        
        self.camera_combo = QComboBox()
        cameras = QMediaDevices.videoInputs()
        if cameras:
            for cam in cameras:
                self.camera_combo.addItem(cam.description())
        else:
            self.camera_combo.addItems(["0", "1", "2", "3"])
            
        hw_layout.addRow("Camera:", self.camera_combo)
        
        main_layout.addWidget(hw_group)
        
        # --- Detection Settings ---
        det_group = QGroupBox("Detection Parameters")
        det_layout = QFormLayout(det_group)
        
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setRange(0, 100)
        self.conf_slider.setSingleStep(1)
        self.conf_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.conf_slider.setTickInterval(10)
        
        self.conf_label = QLabel("30%")
        self.conf_slider.valueChanged.connect(lambda v: self.conf_label.setText(f"{v}%"))
        
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(self.conf_slider)
        conf_layout.addWidget(self.conf_label)
        
        det_layout.addRow("Confidence Threshold:", conf_layout)
        
        self.max_det_spinbox = QSpinBox()
        self.max_det_spinbox.setRange(1, 300)
        self.max_det_spinbox.setValue(100)
        det_layout.addRow("Max Detections:", self.max_det_spinbox)
        
        main_layout.addWidget(det_group)
        
        # --- UI Settings ---
        ui_group = QGroupBox("User Interface")
        ui_layout = QVBoxLayout(ui_group)
        
        self.show_boxes_chk = QCheckBox("Show Bounding Boxes")
        self.show_labels_chk = QCheckBox("Show Labels")
        self.show_conf_chk = QCheckBox("Show Confidence Bars in Sidebar")
        
        ui_layout.addWidget(self.show_boxes_chk)
        ui_layout.addWidget(self.show_labels_chk)
        ui_layout.addWidget(self.show_conf_chk)
        
        main_layout.addWidget(ui_group)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.button_box)

    def load_settings(self):
        # Default settings if none exist
        self.model_combo.setCurrentText(self.settings.value("model_version", "yolo11n", type=str))
        cam_idx = self.settings.value("camera_index", 0, type=int)
        if cam_idx < self.camera_combo.count():
            self.camera_combo.setCurrentIndex(cam_idx)
        
        conf = self.settings.value("confidence_threshold", 30, type=int)
        self.conf_slider.setValue(conf)
        self.conf_label.setText(f"{conf}%")
        
        self.max_det_spinbox.setValue(self.settings.value("max_detections", 100, type=int))
        
        self.show_boxes_chk.setChecked(self.settings.value("show_boxes", True, type=bool))
        self.show_labels_chk.setChecked(self.settings.value("show_labels", True, type=bool))
        self.show_conf_chk.setChecked(self.settings.value("show_conf_bars", True, type=bool))
        
        # Store original model to check if it changes on save
        self.original_model = self.model_combo.currentText()

    def save_settings(self):
        self.settings.setValue("model_version", self.model_combo.currentText())
        self.settings.setValue("camera_index", self.camera_combo.currentIndex())
        self.settings.setValue("confidence_threshold", self.conf_slider.value())
        self.settings.setValue("max_detections", self.max_det_spinbox.value())
        self.settings.setValue("show_boxes", self.show_boxes_chk.isChecked())
        self.settings.setValue("show_labels", self.show_labels_chk.isChecked())
        self.settings.setValue("show_conf_bars", self.show_conf_chk.isChecked())
        
        self.settings.sync()
        
        # Emit signal to notify main window
        self.settings_changed.emit()
        
        # If model changed, notify separately because it requires reloading
        if self.original_model != self.model_combo.currentText():
            self.model_changed.emit(self.model_combo.currentText())
            
        self.accept()
