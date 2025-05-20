import cv2
import numpy as np
import os

def visualize_pose(img, rvec, tvec, camera_matrix, dist_coeffs, axis_len=10.0):
    """
    Visualize the pose of an object in the image using the rotation and translation vectors.
    :param img: Input image.
    :param rvec: Rotation vector.
    :param tvec: Translation vector.
    :param camera_matrix: Camera intrinsic matrix.
    :param dist_coeffs: Camera distortion coefficients.
    :param axis_len: Length of the axes to be drawn.
    :return: Annotated image with axes drawn.
    """
    axes_points = np.array([
        [0, 0, 0],            # Centroid
        [0, axis_len, 0],     # +X (red) -> Swap X and Y
        [-axis_len, 0, 0],    # +Y (green) -> Swap X and Y
        [0, 0, axis_len]      # +Z (blue) (unchanged)
    ], dtype=np.float32)

    image_points, _ = cv2.projectPoints(axes_points, rvec, tvec, camera_matrix, dist_coeffs)
    image_points = np.int32(image_points).reshape(-1, 2)

    centroid = tuple(image_points[0])
    cv2.circle(img, centroid, 5, (255, 255, 255), -1)                # White dot for centroid
    cv2.line(img, centroid, tuple(image_points[1]), (0, 0, 255), 2)  # +X axis (red)
    cv2.line(img, centroid, tuple(image_points[2]), (0, 255, 0), 2)  # +Y axis (green)
    cv2.line(img, centroid, tuple(image_points[3]), (255, 0, 0), 2)  # +Z axis (blue)

    return img

def rvec_to_rpy(rvec):
    """
    Convert rotation vector to roll, pitch, yaw angles.
    :param rvec: Rotation vector.
    :return: Roll, pitch, yaw angles in degrees.
    """
    R, _ = cv2.Rodrigues(rvec)  # Convert rvec to rotation matrix
    sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)

    singular = sy < 1e-6
    if not singular:
        roll = np.arctan2(R[2, 1], R[2, 2])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
    else:
        roll = np.arctan2(-R[1, 2], R[1, 1])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = 0  # Undefined in singular case

    return np.degrees([roll, pitch, yaw])

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

def filter_by_color(frame, lower_bound, upper_bound, min_contour_area=500):
    """
    Filter the frame by color and apply morphological operations to clean up the mask.
    :param frame: Input image frame.
    :param lower_bound: Lower bound for color filtering (HSV).
    :param upper_bound: Upper bound for color filtering (HSV).
    :param min_contour_area: Minimum contour area to keep.
    :return: Filtered frame.
    """
    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create a mask based on color range
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    
    # Morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Close small gaps
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove small noise
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a new mask to keep only large contours
    filtered_mask = np.zeros_like(mask)
    for contour in contours:
        if cv2.contourArea(contour) > min_contour_area:  # Filter by area
            cv2.drawContours(filtered_mask, [contour], -1, 255, thickness=cv2.FILLED)
    
    # Apply the filtered mask to the original frame
    frame = cv2.bitwise_and(frame, frame, mask=filtered_mask)
    # white_frame = np.full_like(frame, 255)

    # # Black pixel replacement
    # frame = np.where(frame == 0, white_frame, frame)

    return frame