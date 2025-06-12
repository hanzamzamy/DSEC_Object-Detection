import argparse
import cv2
import numpy as np
from ultralytics import YOLO

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def is_mp4_file(path):
    """
    Check if the given path is a video file.
    :param path: Path to the file.
    :return: True if the file is a MP4, False otherwise.
    """
    if not os.path.exists(path):
        return False
    # Check for file extensions
    return path.lower().endswith('mp4')

def detect_stream(model_path, confidence, source, headless=False, output=None):
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
    parser = argparse.ArgumentParser(description="YOLO Object Detection Stream")
    parser.add_argument("--detector", required=True, help="Path to YOLO model (e.g., yolov8.pt)")
    parser.add_argument("--confidence", type=float, default=0.7, help="Minimum confidence threshold")
    parser.add_argument("--input", required=True, help="Camera index or path to video file")
    parser.add_argument("--output", help="Output video path (optional)")
    parser.add_argument("--headless", action="store_true", help="Run without GUI display")
    return parser.parse_args()

def main():
    args = parse_args()
    detect_stream(args.detector, args.confidence, args.input, args.headless, args.output)

if __name__ == "__main__":
    main()
