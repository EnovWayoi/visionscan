import os
import time
import cv2
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_name: str = "yolo11n", conf_threshold: float = 0.3):
        """
        Initializes the YOLO object detector. Exports to ONNX if necessary.
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.model = None
        self.class_names = {}
        
        self.load_model(self.model_name)

    def load_model(self, model_name: str):
        """
        Loads the YOLOv11 model, exports to ONNX if .onnx doesn't exist,
        and then loads the ONNX model for inference.
        """
        self.model_name = model_name
        pt_path = f"{self.model_name}.pt"
        onnx_path = f"{self.model_name}.onnx"

        # Load PT to trigger download or export
        print(f"Loading base PyTorch model: {pt_path}")
        pt_model = YOLO(pt_path)
        
        # We need class names for mapping
        self.class_names = pt_model.names

        if not os.path.exists(onnx_path):
            print(f"Exporting {self.model_name} to ONNX format...")
            pt_model.export(format="onnx")
            
        print(f"Loading ONNX model: {onnx_path}")
        # task="detect" is implied, but good to be explicit
        self.model = YOLO(onnx_path, task="detect")
        print("Model loaded successfully.")

    def set_confidence(self, conf: float):
        self.conf_threshold = conf

    def predict(self, frame, show_boxes: bool = True, show_labels: bool = True) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Run inference on a single frame.
        Returns:
            annotated_frame: The frame with bounding boxes drawn by ultralytics
            detections: List of dicts with 'name', 'confidence', 'bbox'
        """
        if self.model is None:
            return frame, []
            
        # Run inference
        # verbose=False to keep stdout clean
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        annotated_frame = frame
        
        if results and len(results) > 0:
            result = results[0]
            annotated_frame = frame.copy()
            
            # Extract detection info for the UI list
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                
                # Bounding box in xyxy format
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                name = self.class_names.get(cls_id, f"Unknown-{cls_id}")
                
                detections.append({
                    "name": name,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })
                
                # Generate a color based on class ID (simple pseudo-randomish color)
                color = ((cls_id * 50) % 255, (cls_id * 120) % 255, (cls_id * 80 + 100) % 255)
                
                if show_boxes:
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    
                if show_labels:
                    label_text = f"{name} {conf:.2f}"
                    # Add background to text
                    (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(annotated_frame, (x1, y1 - th - 5), (x1 + tw, y1), color, -1)
                    cv2.putText(annotated_frame, label_text, (x1, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
        # Sort detections by confidence descending
        detections.sort(key=lambda x: x["confidence"], reverse=True)
                
        return annotated_frame, detections
