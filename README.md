# VisionScan

VisionScan is a real-time object detection desktop application.

## Prerequisites
- Python 3.12+
- `uv` package manager (`pip install uv`)
- (Optional but highly recommended) CUDA Toolkit and cuDNN for ONNX GPU inference

## How to Run

### Windows
Run the provided `run.bat` script:
```cmd
run.bat
```

### macOS / Linux
Run the provided `run.sh` script:
```bash
./run.sh
```

## Features
- YOLOv11 inference with ONNX Runtime
- Custom PyQt6 User Interface
- Real-time performance with FPS counter
- Settings persistence

## Tech Stack
- **Language:** Python 3.12+
- **UI Framework:** PyQt6
- **Computer Vision:** OpenCV (`opencv-python`)
- **Object Detection:** Ultralytics YOLOv11
- **Inference Engine:** ONNX Runtime (GPU accelerated)
- **Package Management:** `uv`
