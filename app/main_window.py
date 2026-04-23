import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QToolBar, QStatusBar, QMessageBox, QComboBox, QSlider,
    QPushButton, QScrollArea, QStyle
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtMultimedia import QMediaDevices

from app.camera_thread import CameraThread
from app.settings_dialog import SettingsDialog
from app.ui_components import DetectionList

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionScan — Real-Time Object Detector")
        self.resize(1000, 700)
        
        # Application Settings
        self.settings = QSettings("VisionScanApp", "Settings")
        
        self.setup_ui()
        
        # Current frames
        self.current_frame_raw = None
        self.current_frame_annotated = None
        
        # Initialize and start camera thread
        self.init_camera()

    def setup_ui(self):
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # --- Left Panel (Camera Feed) ---
        left_panel = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #111111; border-radius: 8px;")
        self.camera_label.setText("Loading Camera & Model...")
        left_panel.addWidget(self.camera_label, stretch=1)
        
        # --- Right Panel (Detections Sidebar) ---
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(5, 0, 5, 0)
        
        sidebar_title = QLabel("Detections")
        sidebar_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        right_panel.addWidget(sidebar_title)
        
        # Badge for total count
        self.count_badge = QLabel("0 objects detected")
        self.count_badge.setStyleSheet("color: #AAAAAA; font-size: 12px; margin-bottom: 10px;")
        right_panel.addWidget(self.count_badge)
        
        # Detection List Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(240)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.detection_list = DetectionList()
        scroll_area.setWidget(self.detection_list)
        right_panel.addWidget(scroll_area)
        
        # Add to main layout
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel)
        
        # --- Toolbar ---
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Camera Selector
        self.toolbar.addWidget(QLabel(" Cam: "))
        self.cam_selector = QComboBox()
        
        # Populate with actual camera names using QMediaDevices
        cameras = QMediaDevices.videoInputs()
        if cameras:
            for cam in cameras:
                self.cam_selector.addItem(cam.description())
        else:
            self.cam_selector.addItems(["0", "1", "2", "3"])
            
        saved_idx = self.settings.value("camera_index", 0, type=int)
        if saved_idx < self.cam_selector.count():
            self.cam_selector.setCurrentIndex(saved_idx)
            
        self.cam_selector.currentIndexChanged.connect(self.on_camera_selected)
        self.toolbar.addWidget(self.cam_selector)
        
        self.toolbar.addSeparator()
        
        # Confidence Slider
        self.toolbar.addWidget(QLabel(" Conf: "))
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setRange(0, 100)
        self.conf_slider.setFixedWidth(100)
        conf_val = self.settings.value("confidence_threshold", 30, type=int)
        self.conf_slider.setValue(conf_val)
        self.conf_slider.valueChanged.connect(self.on_conf_changed)
        self.toolbar.addWidget(self.conf_slider)
        
        self.conf_label_tb = QLabel(f" {conf_val}% ")
        self.toolbar.addWidget(self.conf_label_tb)
        
        self.toolbar.addSeparator()
        
        # Play/Pause Button
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setCheckable(True)
        self.btn_pause.toggled.connect(self.on_pause_toggled)
        self.toolbar.addWidget(self.btn_pause)
        
        # Screenshot Button
        self.btn_screenshot = QPushButton("Screenshot")
        self.btn_screenshot.clicked.connect(self.take_screenshot)
        self.toolbar.addWidget(self.btn_screenshot)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Settings Button
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.btn_settings.clicked.connect(self.open_settings)
        self.toolbar.addWidget(self.btn_settings)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.lbl_fps = QLabel("FPS: --")
        self.lbl_res = QLabel("Res: --x--")
        self.lbl_model = QLabel(f"Model: {self.settings.value('model_version', 'yolo11n', type=str)}")
        
        self.status_bar.addWidget(self.lbl_fps)
        self.status_bar.addWidget(QLabel(" | "))
        self.status_bar.addWidget(self.lbl_res)
        self.status_bar.addWidget(QLabel(" | "))
        self.status_bar.addWidget(self.lbl_model)

    def init_camera(self):
        cam_idx = self.settings.value("camera_index", 0, type=int)
        model = self.settings.value("model_version", "yolo11n", type=str)
        conf = self.settings.value("confidence_threshold", 30, type=int) / 100.0
        
        self.camera_thread = CameraThread(camera_index=cam_idx, model_name=model, conf_threshold=conf)
        self.camera_thread.set_draw_options(
            self.settings.value("show_boxes", True, type=bool),
            self.settings.value("show_labels", True, type=bool)
        )
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.error_occurred.connect(self.show_error)
        self.camera_thread.start()

    def update_frame(self, raw_frame, annotated_frame, detections, fps):
        self.current_frame_raw = raw_frame
        self.current_frame_annotated = annotated_frame
        
        # Update UI text
        self.lbl_fps.setText(f"FPS: {fps:.1f}")
        h, w = raw_frame.shape[:2]
        self.lbl_res.setText(f"Res: {w}x{h}")
        self.count_badge.setText(f"{len(detections)} objects detected")
        
        # Convert annotated frame to QPixmap and display
        rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        # Scale pixmap to fit the label, keeping aspect ratio
        scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.camera_label.setPixmap(scaled_pixmap)
        
        # Update Detections sidebar if enabled
        if self.settings.value("show_conf_bars", True, type=bool):
            self.detection_list.update_detections(detections)
        else:
            self.detection_list.clear()

    def show_error(self, message):
        self.status_bar.showMessage(message, 5000)
        self.camera_label.setText(f"Error: {message}")

    def on_camera_selected(self, index):
        cam_idx = index
        self.settings.setValue("camera_index", cam_idx)
        if hasattr(self, 'camera_thread'):
            self.camera_thread.set_camera(cam_idx)

    def on_conf_changed(self, value):
        self.conf_label_tb.setText(f" {value}% ")
        self.settings.setValue("confidence_threshold", value)
        if hasattr(self, 'camera_thread'):
            self.camera_thread.set_threshold(value / 100.0)

    def on_pause_toggled(self, checked):
        if hasattr(self, 'camera_thread'):
            self.camera_thread.set_paused(checked)
        self.btn_pause.setText("Resume" if checked else "Pause")

    def take_screenshot(self):
        if self.current_frame_annotated is None:
            return
            
        screenshot_dir = r"D:\project\visionscan\screenshot"
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = os.path.join(screenshot_dir, f"VisionScan_{cv2.getTickCount()}.png")
        
        cv2.imwrite(filename, self.current_frame_annotated)
        self.status_bar.showMessage(f"Saved screenshot to {filename}", 3000)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.apply_settings)
        dialog.model_changed.connect(self.apply_model_change)
        dialog.exec()

    def apply_settings(self):
        # Sync values from settings to UI elements in toolbar
        conf = self.settings.value("confidence_threshold", 30, type=int)
        self.conf_slider.setValue(conf)
        
        cam_idx = self.settings.value("camera_index", 0, type=int)
        if self.cam_selector.currentIndex() != cam_idx and cam_idx < self.cam_selector.count():
            self.cam_selector.setCurrentIndex(cam_idx)
            
        if hasattr(self, 'camera_thread'):
            self.camera_thread.set_draw_options(
                self.settings.value("show_boxes", True, type=bool),
                self.settings.value("show_labels", True, type=bool)
            )

    def apply_model_change(self, new_model):
        self.lbl_model.setText(f"Model: {new_model}")
        self.status_bar.showMessage(f"Loading {new_model}...", 3000)
        if hasattr(self, 'camera_thread'):
            self.camera_thread.set_model(new_model)

    def closeEvent(self, event):
        if hasattr(self, 'camera_thread'):
            self.camera_thread.stop()
        event.accept()
