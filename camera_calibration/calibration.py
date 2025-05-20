import cv2
import numpy as np
import argparse

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Camera calibration using video frames of a checkerboard pattern.")
    parser.add_argument("video_path", help="Path to the input video file.")
    parser.add_argument("--size", "-s", type=float, default=10, help="Size of a square in the checkerboard (default: 10mm).")
    parser.add_argument("--row", "-r", type=int, required=True, help="Number of inner corners along the rows of the checkerboard.")
    parser.add_argument("--col", "-c", type=int, required=True, help="Number of inner corners along the columns of the checkerboard.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output for detailed debug information.")
    parser.add_argument("--jump", "-j", type=int, default=0, help="Number of frames to skip between processing (default: 0).")
    parser.add_argument("--limit", "-l", type=int, default=0, help="Number of maximum frames for calibration. Use zero to disable (default: 0).")
    args = parser.parse_args()

    # Checkerboard size
    checkerboard_size = (args.col, args.row)
    square_size = args.size

    # Termination criteria for corner sub-pixel accuracy
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare object points
    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    # Arrays to store object points and image points
    objpoints = []  # 3D points in real world space
    imgpoints = []  # 2D points in image plane

    # Load the video
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        print("Error: Unable to open video file.")
        exit()

    good_frames = 0
    bad_frames = 0
    frame_index = 0

    while True:
        if args.limit > 0 and frame_index >= args.limit:
            break

        ret, frame = cap.read()
        if not ret:
            break

        # Skip frames if jump is greater than 0
        if args.jump > 0 and frame_index % (args.jump + 1) != 0:
            frame_index += 1
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Find the checkerboard corners
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

        if ret:
            good_frames += 1
            if args.verbose:
                print(f"[Frame {frame_index}] Checkerboard detected.")
            objpoints.append(objp)
            # Refine corner positions
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            if args.verbose:
                cv2.drawChessboardCorners(frame, checkerboard_size, corners2, ret)
                cv2.imshow('Checkerboard', frame)
                cv2.waitKey(1)
        else:
            bad_frames += 1
            if args.verbose:
                print(f"[Frame {frame_index}] Checkerboard NOT detected.")

        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()

    # Perform camera calibration
    if objpoints and imgpoints:
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        print("Camera calibration completed.")
        print("Camera matrix:\n", camera_matrix)
        print("Distortion coefficients:\n", dist_coeffs)
        np.savez("camera_calibration", camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
    else:
        print("No valid checkerboard patterns were detected. Calibration failed.")

    # Summary
    print(f"\nSummary:")
    print(f"  Total frames processed: {frame_index}")
    print(f"  Good frames (checkerboard detected): {good_frames}")
    print(f"  Bad frames (no checkerboard): {bad_frames}")

if __name__ == "__main__":
    main()
