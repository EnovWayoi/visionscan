import time
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from app.detector import ObjectDetector

class CameraThread(QThread):
    # Signals to communicate with the main UI thread
    # Emits original frame (for screenshot), annotated frame, detections dict, and FPS
    frame_ready = pyqtSignal(object, object, list, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index=0, model_name="yolo11n", conf_threshold=0.3):
        super().__init__()
        self.camera_index = camera_index
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        
        self.show_boxes = True
        self.show_labels = True
        
        self.running = True
        self.paused = False
        self.cap = None
        self.detector = None
        
        # Performance/skip frames
        self.skip_frames = False
        self.frame_count = 0
        
    def run(self):
        try:
            # Initialize detector
            self.detector = ObjectDetector(model_name=self.model_name, conf_threshold=self.conf_threshold)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load model: {str(e)}")
            return

        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            # Try to request 720p resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            if not self.cap.isOpened():
                self.error_occurred.emit(f"Could not open camera {self.camera_index}")
                return
        except Exception as e:
            self.error_occurred.emit(f"Camera error: {str(e)}")
            return

        prev_time = time.time()
        
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                self.error_occurred.emit("Failed to grab frame")
                time.sleep(0.1)
                continue

            self.frame_count += 1
            current_time = time.time()
            fps = 1 / (current_time - prev_time) if current_time > prev_time else 0
            
            # Simple frame skipping if FPS drops below 20
            # If skipping is active, only run inference every 2nd frame
            run_inference = True
            if fps < 20 and fps > 0:
                self.skip_frames = True
            elif fps > 25:
                self.skip_frames = False
                
            if self.skip_frames and self.frame_count % 2 != 0:
                run_inference = False

            try:
                if run_inference:
                    annotated_frame, detections = self.detector.predict(frame, self.show_boxes, self.show_labels)
                else:
                    # Just pass the raw frame without detections if skipping
                    annotated_frame = frame
                    detections = []
                    
                prev_time = current_time
                self.frame_ready.emit(frame, annotated_frame, detections, fps)
                
            except Exception as e:
                self.error_occurred.emit(f"Inference error: {str(e)}")
                time.sleep(1) # Prevent spamming

        # Cleanup
        if self.cap:
            self.cap.release()

    def stop(self):
        self.running = False
        self.wait()

    def set_paused(self, paused: bool):
        self.paused = paused

    def set_camera(self, index: int):
        self.camera_index = index
        if self.cap:
            self.cap.release()
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def set_model(self, model_name: str):
        self.model_name = model_name
        if self.detector:
            try:
                self.detector.load_model(self.model_name)
            except Exception as e:
                self.error_occurred.emit(f"Failed to change model: {str(e)}")

    def set_threshold(self, conf: float):
        self.conf_threshold = conf
        if self.detector:
            self.detector.set_confidence(self.conf_threshold)

    def set_draw_options(self, show_boxes: bool, show_labels: bool):
        self.show_boxes = show_boxes
        self.show_labels = show_labels
