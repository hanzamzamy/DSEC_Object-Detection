import cv2
import numpy as np
import argparse
import os
import glob

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Camera calibration using video frames or image files of a checkerboard pattern.")
    parser.add_argument("--video_path", "-v", help="Path to the input video file.")
    parser.add_argument("--image_dir", "-i", help="Path to the directory containing checkerboard images.")
    parser.add_argument("--size", "-s", type=float, default=10, help="Size of a square in the checkerboard (default: 10mm).")
    parser.add_argument("--row", "-r", type=int, required=True, help="Number of inner corners along the rows of the checkerboard.")
    parser.add_argument("--col", "-c", type=int, required=True, help="Number of inner corners along the columns of the checkerboard.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for detailed debug information.")
    parser.add_argument("--jump", "-j", type=int, default=0, help="Number of frames to skip between processing (only applies to video).")
    parser.add_argument("--limit", "-l", type=int, default=0, help="Maximum number of frames or images to process (0 for no limit).")
    args = parser.parse_args()

    if not args.video_path and not args.image_dir:
        print("Error: Please specify either --video_path or --image_dir.")
        exit()

    checkerboard_size = (args.col, args.row)
    square_size = args.size

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = []
    imgpoints = []

    good_frames = 0
    bad_frames = 0
    frame_index = 0

    if args.image_dir:
        # Process images
        image_paths = sorted(glob.glob(os.path.join(args.image_dir, '*.*')))
        for path in image_paths:
            if args.limit > 0 and frame_index >= args.limit:
                break

            img = cv2.imread(path)
            if img is None:
                if args.verbose:
                    print(f"[{frame_index}] Failed to load image: {path}")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

            if ret:
                good_frames += 1
                if args.verbose:
                    print(f"[Image {frame_index}] Checkerboard detected: {path}")
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners2)

                if args.verbose:
                    cv2.drawChessboardCorners(img, checkerboard_size, corners2, ret)
                    cv2.imshow('Checkerboard', img)
                    cv2.waitKey(100)
            else:
                bad_frames += 1
                if args.verbose:
                    print(f"[Image {frame_index}] Checkerboard NOT detected: {path}")
            frame_index += 1

    elif args.video_path:
        # Process video
        cap = cv2.VideoCapture(args.video_path)
        if not cap.isOpened():
            print("Error: Unable to open video file.")
            exit()

        while True:
            if args.limit > 0 and frame_index >= args.limit:
                break

            ret, frame = cap.read()
            if not ret:
                break

            if args.jump > 0 and frame_index % (args.jump + 1) != 0:
                frame_index += 1
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

            if ret:
                good_frames += 1
                if args.verbose:
                    print(f"[Frame {frame_index}] Checkerboard detected.")
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners2)

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

    # Calibration
    if objpoints and imgpoints:
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)
        print("\nCamera calibration completed.")
        print("Camera matrix:\n", camera_matrix)
        print("Distortion coefficients:\n", dist_coeffs)
        np.savez("camera_calibration", camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
    else:
        print("No valid checkerboard patterns were detected. Calibration failed.")

    print(f"\nSummary:")
    print(f"  Total frames/images processed: {frame_index}")
    print(f"  Good detections: {good_frames}")
    print(f"  Failed detections: {bad_frames}")

if __name__ == "__main__":
    main()
