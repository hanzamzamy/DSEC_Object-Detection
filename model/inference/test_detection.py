import argparse
import os
import cv2
import numpy as np
from ultralytics import YOLO

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def is_mp4_file(path):
    """
    Check if the given path points to an MP4 video file.
    
    Args:
        path (str): Path to the file to check
        
    Returns:
        bool: True if the file exists and has an MP4 extension, False otherwise
        
    Note:
        This function only checks the file extension and existence, not the actual file content.
    """
    if not os.path.exists(path):
        return False
    # Check for file extensions
    return path.lower().endswith('mp4')

def detect_stream(model_path, confidence, source, headless=False, output=None):
    """
    Run object detection on a video stream or file using a YOLO model.
    
    This function processes frames from the specified source, performs object detection 
    on each frame using the provided YOLO model, and optionally displays or saves the 
    results with bounding box annotations.
    
    Args:
        model_path (str): Path to the YOLO model file
        confidence (float): Minimum confidence threshold for detections (0.0-1.0)
        source (str or int): Path to video file or camera index
        headless (bool, optional): If True, run without displaying GUI. Defaults to False.
        output (str, optional): Path to save output video. Defaults to None.
        
    Note:
        - Press 'q' to quit the stream when display is enabled
        - Stream will end when video file ends or camera disconnects
    """
    model = YOLO(model_path)
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[ERR] Cannot open video source.")
        return

    writer = None
    if output and is_mp4_file(source):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        writer = cv2.VideoWriter(output, fourcc, fps, size)

    print("[INF] Starting detection stream...")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERR] Failed to read frame.")
                break

            results = model.predict(frame, conf=confidence, imgsz=(FRAME_WIDTH, FRAME_HEIGHT))
            annotated = results[0].plot()

            if not headless:
                cv2.imshow("YOLO Detection", annotated)

            if writer:
                writer.write(annotated)

            if not headless:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

    finally:
        cap.release()
        if writer:
            writer.release()
        if not headless:
            cv2.destroyAllWindows()
        print("[INF] Stream ended.")

def parse_args():
    """
    Parse command line arguments for the YOLO detection script.
    
    Sets up argument parsing for:
    - detector: Path to YOLO model file
    - confidence: Detection confidence threshold
    - input: Video source (file path or camera index)
    - output: Optional path to save output video
    - headless: Flag to run without GUI display
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
        
    Example usage:
        python test_detection.py --detector yolov8n.pt --confidence 0.5 --input video.mp4 --output results.mp4
    """
    parser = argparse.ArgumentParser(description="YOLO Object Detection Stream")
    parser.add_argument("--detector", required=True, help="Path to YOLO model (e.g., yolov8.pt)")
    parser.add_argument("--confidence", type=float, default=0.7, help="Minimum confidence threshold")
    parser.add_argument("--input", required=True, help="Camera index or path to video file")
    parser.add_argument("--output", help="Output video path (optional)")
    parser.add_argument("--headless", action="store_true", help="Run without GUI display")
    return parser.parse_args()

def main():
    """
    Main entry point for the YOLO detection script.
    
    Parses command line arguments and runs the detection stream with the specified
    parameters. This function serves as the primary entry point when the script
    is run directly.
    
    Flow:
        1. Parse command-line arguments
        2. Run object detection on the specified video source
        3. Display and/or save results based on provided options
    """
    args = parse_args()
    detect_stream(args.detector, args.confidence, args.input, args.headless, args.output)

if __name__ == "__main__":
    main()
