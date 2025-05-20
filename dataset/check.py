import os
import cv2
import argparse

def visualize_labels(dataset_name, output_dir):
    image_dirs = [f"./{dataset_name}/train/images", f"./{dataset_name}/val/images"]
    label_dirs = [f"./{dataset_name}/train/labels", f"./{dataset_name}/val/labels"]
    os.makedirs(output_dir, exist_ok=True)

    # Define consistent colors for the 9 keypoints
    keypoint_colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (255, 128, 0), (128, 0, 255), (0, 128, 255)
    ]

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

                if len(data) > 5:
                    keypoints = list(map(float, data[5:]))

                    for i in range(0, len(keypoints), 3):
                        if i + 2 >= len(keypoints):
                            break  # Avoid out-of-bounds
                        px = int(keypoints[i] * width)
                        py = int(keypoints[i + 1] * height)
                        visibility = int(keypoints[i + 2])
                        if visibility > 0 and (i // 3) < len(keypoint_colors):
                            color = keypoint_colors[i // 3]
                            cv2.circle(image, (px, py), 5, color, -1)
                            cv2.putText(image, str(i // 3 + 1), (px + 5, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            out_path = os.path.join(output_dir, image_file)
            cv2.imwrite(out_path, image)

    print(f"Visualized images are saved in {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize YOLO labels: detection and optional keypoints.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name (e.g., 'output')")
    parser.add_argument("--outdir", type=str, default="./result", help="Directory to save visualized images")

    args = parser.parse_args()
    visualize_labels(args.dataset, args.outdir)
