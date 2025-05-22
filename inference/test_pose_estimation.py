import argparse
import cv2
import numpy as np
from ultralytics import YOLO
import os

from model import PoseEstimationModel
# from filter import PoseKalmanFilter
from utility import visualize_pose, is_mp4_file, filter_by_color

pose_estimation_model = None

FRAME_WIDTH = 640
FRAME_HEIGHT = 480  # Ratio of webcam: 4:3

# Orange color filter
orange_lower_bound = np.array([0, 100, 100])
orange_upper_bound = np.array([20, 255, 255])

# Object dimensions (mm)
real_dims = [49.0, 86.2, 94.4]
dummy_dims = [48.7, 61.0, 81.0]
cookie_dims = [44.5, 44.5, 11,7]
pouch_dims = [181, 44.7, 44.5]

def video_stream(source, headless=False, output=None):
    # Webcam or video initialization
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[ERR] Failed to open video.")
        return

    # Video writer initialization if output is specified
    writer = None
    if output and is_mp4_file(source):  # Only write if input is a video file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        writer = cv2.VideoWriter(output, fourcc, fps, frame_size)

    print("[INF] Starting video stream.")
    paused = False

    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("[ERR] Cannot read frame.")
                    break

                annotated_frame, frame_rvecs, frame_tvecs = pose_estimation_model.estimate_pose(
                    frame, frame
                )

                if len(frame_rvecs) == len(frame_tvecs) or len(frame_rvecs) != 0 or len(frame_tvecs) != 0:
                    # Display result as axis overlay
                    
                    for rvec, tvec in zip(frame_rvecs, frame_tvecs):
                        annotated_frame = visualize_pose(
                            annotated_frame, rvec, tvec, 
                            pose_estimation_model.camera_matrix,
                            pose_estimation_model.dist_coeffs) 

                if not headless:
                    cv2.imshow('Visualization', annotated_frame)

                if writer:
                    print("[INF] Writing frame to output video.")
                    writer.write(annotated_frame)

            if not headless:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("[INF] Quitting...")
                    break
                elif key == ord('p'):
                    paused = True
                    print("[INF] Paused")
                elif key == ord('r'):
                    paused = False
                    print("[INF] Resumed")

    finally:
        cap.release()
        if writer:
            writer.release()
        if not headless:
            cv2.destroyAllWindows()
        print("[INF] Stream stopped.")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stream camera inference using OpenCV GUI."
    )
    parser.add_argument(
        "--detector",
        required=True,
        help="Path to YOLO model file (e.g., /path/to/model.pt)."
    )
    parser.add_argument(
        "--calibration",
        required=True,
        help="Path to .npz calibration data (e.g., /path/to/calibration.npz)."
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.7,
        help="Confidence threshold for inference (default: 0.7)."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Camera device (e.g., /dev/video0) or video file (e.g., video.mp4)."
    )
    parser.add_argument(
        "--output",
        help="Path to save the output video (e.g., /path/to/output.mp4)."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without displaying GUI window."
    )
    return parser.parse_args()

def main():
    global pose_estimation_model

    # Parse arguments
    args = parse_arguments()

    # Load camera calibration data
    data = np.load(args.calibration)
    camera_matrix = data['camera_matrix']
    dist_coeffs = data['dist_coeffs']

    # Initialize pose estimation model
    pose_estimation_model = PoseEstimationModel(
        model_path=args.detector,
        min_conf=args.confidence,
        input_size=(FRAME_WIDTH, FRAME_HEIGHT),
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )

    pose_estimation_model.add_object('cookie', cookie_dims)

    # Start webcam or video stream
    video_stream(args.input, args.headless, args.output)

if __name__ == "__main__":
    main()
