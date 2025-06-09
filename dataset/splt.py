import os
import shutil
import random
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Split dataset for YOLO keypoint training")
    parser.add_argument("--datasource_path", type=str, required=True, help="Path to the source dataset directory")
    parser.add_argument("--dataset_name", type=str, required=True, help="Name of the dataset (used as output folder and YAML filename)")
    parser.add_argument("--split_ratio", type=float, default=0.8, help="Train split ratio (default: 0.8)")
    parser.add_argument("--label_type", type=str, required=True, choices=[
        "label_vertice", "label_vertice_obscured", "label_cuboid", "label_cuboid_obscured"
    ], help="Type of label to use")
    return parser.parse_args()

def create_dirs(base_path):
    paths = {
        "train_images": os.path.join(base_path, "train/images"),
        "val_images": os.path.join(base_path, "val/images"),
        "train_labels": os.path.join(base_path, "train/labels"),
        "val_labels": os.path.join(base_path, "val/labels")
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths

def split_and_copy_images(images_root, subdirs, split_ratio, output_paths):
    for subdir in subdirs:
        subdir_path = os.path.join(images_root, subdir)
        images = [f for f in os.listdir(subdir_path) if f.endswith(".jpg")]
        random.shuffle(images)

        split_point = int(len(images) * split_ratio)
        train_images = images[:split_point]
        val_images = images[split_point:]

        for img in train_images:
            new_name = f"{subdir}-{img}"
            shutil.copy(os.path.join(subdir_path, img), os.path.join(output_paths["train_images"], new_name))

        for img in val_images:
            new_name = f"{subdir}-{img}"
            shutil.copy(os.path.join(subdir_path, img), os.path.join(output_paths["val_images"], new_name))

def copy_labels(images_dir, destination, label_root):
    for img_file in os.listdir(images_dir):
        if img_file.endswith(".jpg"):
            img_id = img_file.split("-")[-1].split(".")[0]
            subdir = img_file.split("-")[0]

            if "BG_" not in img_file:
                label_file = os.path.join(label_root, f"{img_id}.txt")
            else:
                label_file = os.path.join(os.path.dirname(label_root), "label_bg", "bg.txt")

            if os.path.exists(label_file):
                new_label_name = f"{subdir}-{img_id}.txt"
                shutil.copy(label_file, os.path.join(destination, new_label_name))

def generate_yaml(dataset_path, dataset_name):
    yaml_content =f"""train: ./train/images
val: ./val/images

nc: 1
names:
0: cookie
"""
    yaml_path = os.path.join(dataset_path, f"{dataset_name}.yaml")
    with open(yaml_path, "w") as yaml_file:
        yaml_file.write(yaml_content)

def main():
    args = parse_args()

    # Exported variables
    datasource_path = args.datasource_path
    dataset_name = args.dataset_name
    split_ratio = args.split_ratio
    label_type = args.label_type

    # Derived paths
    images_root = os.path.join(datasource_path, "images")
    labels_root = os.path.join(datasource_path, "labels", label_type)
    dataset_path = os.path.join(".", dataset_name)

    print(f"Splitting dataset from: {datasource_path}")
    print(f"Label type: {label_type}")
    print(f"Saving to: {dataset_path}")
    print(f"Train/Val split ratio: {split_ratio}")

    # Create output directories
    output_paths = create_dirs(dataset_path)

    # Get list of subdirectories under images
    subdirs = [d for d in os.listdir(images_root) if os.path.isdir(os.path.join(images_root, d))]

    # Copy images
    split_and_copy_images(images_root, subdirs, split_ratio, output_paths)

    # Copy labels
    copy_labels(output_paths["train_images"], output_paths["train_labels"], labels_root)
    copy_labels(output_paths["val_images"], output_paths["val_labels"], labels_root)

    # Generate YAML
    generate_yaml(dataset_path, dataset_name)

    print("Dataset split and export complete.")

if __name__ == "__main__":
    main()
