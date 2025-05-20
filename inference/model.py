import cv2
import numpy as np
from ultralytics import YOLO

class PoseEstimationModel:
    def __init__(self, model_path, min_conf, input_size, camera_matrix, dist_coeffs):
        """
        Initialize the PoseEstimationModel with the given parameters.
        :param model_path: Path to the YOLO model file.
        :param min_conf: Minimum confidence threshold for detection."
        :param input_size: Size of the input image for the model.
        :param camera_matrix: Camera matrix for PnP solver.
        :param dist_coeffs: Distortion coefficients for undistortion.
        """
        self.model = YOLO(model_path)
        self.min_conf = min_conf
        self.input_size = input_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.conf_th = min_conf
        self.registered_obj = []

    def add_object(self, obj_name, obj_dim):
        """
        Add a new object to the model.
        :param obj_name: Name of the object.
        :param obj_dim: Dimensions of the object with format [X,Y,Z].
        """
        self.registered_obj.append({
            'name': obj_name,
            'dim': obj_dim
        })
        print(f"Object {obj_name} with dimensions {obj_dim} added.")
        
    def remove_object(self, obj_name):
        """
        Remove an object from the model.
        :param obj_name: Name of the object to be removed.
        """
        self.registered_obj = [obj for obj in self.registered_obj if obj['name'] != obj_name]
        print(f"Object {obj_name} removed.")
        if not self.registered_obj:
            print("No objects registered.")
            return
        print(f"Remaining objects: {[obj['name'] for obj in self.registered_obj]}")

    def get_object_3D_points(self, obj_idx):
        """
        Get the 3D points of the object based on its index.
        :param obj_idx: Index of the object in the registered_obj list.
        :return: 3D points of the object.
        """

        """
        KEYPOINT MAP
        1: front-base-right
        2: front-top-right
        3: back-top-right
        4: back-base-right
        5: front-base-left
        6: front-top-left
        7: back-top-left
        8: back-base-left
        9: centroid

        AXIS DIRECTION
        +X: away
        +Y: left
        +Z: up
        NOTE: Use camera PoV as reference. Physics 3D axis rule (Screwdriver rule).
        """

        """
        TODO: Reevaluate axis convention. Dimension specified as
        [0] X: left-right
        [1] Y: front-back
        [2] Z: up-down
        """
        # Extract dimensions
        length = self.registered_obj[obj_idx]['dim'][0]  # Along +X
        width = self.registered_obj[obj_idx]['dim'][1]   # Along +Y
        height = self.registered_obj[obj_idx]['dim'][2]  # Along +Z

        # Define 3D object points (cuboid corners + centroid)
        object_points = np.array([
            [ length/2, -width/2, -height/2],  # 1: front-base-right
            [ length/2, -width/2,  height/2],  # 2: front-top-right
            [ length/2,  width/2,  height/2],  # 3: back-top-right
            [ length/2,  width/2, -height/2],  # 4: back-base-right
            [-length/2, -width/2, -height/2],  # 5: front-base-left
            [-length/2, -width/2,  height/2],  # 6: front-top-left
            [-length/2,  width/2,  height/2],  # 7: back-top-left
            [-length/2,  width/2, -height/2],  # 8: back-base-left
            [ 0,         0,         0],        # 9: centroid
        ], dtype=np.float32)

        return object_points
    
    def detect_objects(self, image, image_to_plot=None):
        """
        Detect objects in the image using the YOLO model.
        :param image: Input image.
        :param image_to_plot: Image to plot the results on.
        :return: Detected object classes, keypoints, and annotated image.
        """
        results = self.model.predict(image, conf=self.conf_th, imgsz=self.input_size)

        annotated_image = results[0].plot(img=image_to_plot)
        object_classes = results[0].boxes.cls.cpu().numpy().astype(int)
        object_keypoints = results[0].keypoints.xy.cpu().numpy()

        return object_classes, object_keypoints, annotated_image
    
    def estimate_pose(self, image, image_to_plot=None):
        """
        Estimate the pose of the detected objects in the image.
        :param image: Input image.
        :return: Annotated image, rotation vectors, and translation vectors.
        """
        object_classes, object_keypoints, annotated_image = self.detect_objects(image, image_to_plot)

        frame_rvecs = []
        frame_tvecs = []

        for obj_class, keypoints in zip(object_classes, object_keypoints):
            if len(keypoints) < 9:
                return annotated_image, [], []
            
            object_points = self.get_object_3D_points(obj_class)

            pnp_ok, rvec, tvec, _ = cv2.solvePnPRansac(
                object_points,
                keypoints,
                self.camera_matrix,
                self.dist_coeffs,
                reprojectionError=100.0,
                useExtrinsicGuess=False,
                iterationsCount=1000
            )

            if pnp_ok:
                frame_rvecs.append(rvec)
                frame_tvecs.append(tvec)

                print('RVec', rvec.flatten())
                print('TVec', tvec.flatten())
                
        
        return annotated_image, frame_rvecs, frame_tvecs
