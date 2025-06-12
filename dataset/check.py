import os
import cv2
import argparse

def visualize_labels(dataset_name, output_dir):
    """
    Visualize YOLO object detection labels on images.
    
    This function processes images from train and validation sets, drawing bounding boxes
    around detected objects and visualizing keypoints if they exist in the annotation.
    Each processed image is saved to the output directory with annotations overlaid.
    
    Args:
        dataset_name (str): Name of the dataset folder (e.g., 'oreo_dataset')
        output_dir (str): Directory where visualized images will be saved
    """
    image_dirs = [f"./{dataset_name}/train/images", f"./{dataset_name}/val/images"]
    label_dirs = [f"./{dataset_name}/train/labels", f"./{dataset_name}/val/labels"]
    os.makedirs(output_dir, exist_ok=True)

    for img_dir, lbl_dir in zip(image_dirs, label_dirs):
        for image_file in os.listdir(img_dir):
            if not image_file.endswith(".jpg"):
                continue

            image_path = os.path.join(img_dir, image_file)
            label_path = os.path.join(lbl_dir, image_file.replace(".jpg", ".txt"))

            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not read image {image_file}")
                continue

            height, width, _ = image.shape

            if not os.path.exists(label_path):
                print(f"Label file not found for {image_file} in {lbl_dir}")
                continue

            with open(label_path, "r") as file:
                lines = file.readlines()

            for line in lines:
                data = line.strip().split()
                if len(data) < 5:
                    continue

                class_index = int(data[0])
                x_center, y_center, w, h = map(float, data[1:5])

                # Denormalize bounding box
                x1 = int((x_center - w / 2) * width)
                y1 = int((y_center - h / 2) * height)
                x2 = int((x_center + w / 2) * width)
                y2 = int((y_center + h / 2) * height)

                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"Class {class_index}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            out_path = os.path.join(output_dir, image_file)
            cv2.imwrite(out_path, image)

    print(f"Visualized images are saved in {output_dir}")


if __name__ == "__main__":
    """
    Command-line interface for the visualization script.

    This block sets up command-line argument parsing for:
    - dataset: Name of the YOLO dataset to visualize (required)
    - outdir: Directory where visualized images will be saved (default: './result')

    Example usage:
        python check.py --dataset oreo_dataset --outdir ./visualization_results
    """
    parser = argparse.ArgumentParser(description="Visualize YOLO labels: detection and optional keypoints.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name (e.g., 'output')")
    parser.add_argument("--outdir", type=str, default="./result", help="Directory to save visualized images")

    args = parser.parse_args()
    visualize_labels(args.dataset, args.outdir)
