import os
import shutil
import random
import argparse
from pathlib import Path

def parse_args():
    """
    Parse command line arguments for the dataset splitting script.
    
    Sets up argument parsing for required and optional parameters:
    - datasource_path: Path to the source dataset directory
    - dataset_name: Name for the output dataset folder and YAML file
    - split_ratio: Ratio for train/val split (default: 0.8)
    - label_type: Type of label format to use from available options
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Split dataset for YOLO keypoint training")
    parser.add_argument("--datasource_path", type=str, required=True, help="Path to the source dataset directory")
    parser.add_argument("--dataset_name", type=str, required=True, help="Name of the dataset (used as output folder and YAML filename)")
    parser.add_argument("--split_ratio", type=float, default=0.8, help="Train split ratio (default: 0.8)")
    parser.add_argument("--label_type", type=str, required=True, choices=[
        "label_vertice", "label_vertice_obscured", "label_cuboid", "label_cuboid_obscured"
    ], help="Type of label to use")
    return parser.parse_args()

def create_dirs(base_path):
    """
    Create the standard YOLO directory structure for training.
    
    Creates the following directory structure:
    base_path/
    ├── train/
    │   ├── images/
    │   └── labels/
    └── val/
        ├── images/
        └── labels/
    
    Args:
        base_path (str): Base directory where the dataset structure will be created
        
    Returns:
        dict: Dictionary containing paths to all created directories:
            - train_images: Path to training images directory
            - val_images: Path to validation images directory
            - train_labels: Path to training labels directory
            - val_labels: Path to validation labels directory
    
    Note:
        All directories are created with exist_ok=True to prevent errors
        if the directories already exist.
    """
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
    """
    Split images from multiple subdirectories and copy them to train/val directories.
    
    For each subdirectory:
    1. Lists all JPG images
    2. Randomly shuffles the images
    3. Splits images according to the provided ratio
    4. Copies to train/val directories with modified filenames that preserve source information
    
    Args:
        images_root (str): Root directory containing image subdirectories
        subdirs (list): List of subdirectory names to process
        split_ratio (float): Ratio of images to use for training (0.0-1.0)
        output_paths (dict): Dictionary containing paths to output directories
            - train_images: Path where training images will be copied
            - val_images: Path where validation images will be copied
    
    Notes:
        - Destination filenames are prefixed with subdirectory name: "{subdir}-{original_name}"
        - This naming scheme allows for tracking the image source while ensuring uniqueness
    """
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
    """
    Copy label files to match the corresponding images in the dataset.
    
    For each image file:
    1. Extracts the image ID from the filename
    2. Determines the corresponding label file path
    3. Copies the label file to the destination with a matching name pattern
    
    This function handles special cases for background images:
    - Regular images use labels from {label_root}/{img_id}.txt
    - Background images (prefixed with "BG_") use a special "bg.txt" label file
    
    Args:
        images_dir (str): Directory containing image files
        destination (str): Directory where label files should be copied
        label_root (str): Root directory containing source label files
    
    Note:
        The function expects image filenames in the format "{subdir}-{original_name}"
        where the original name contains the numeric ID used for label lookup.
    """
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
    """
    Generate a YAML configuration file for YOLO training.
    
    Creates a YAML file with the following content:
    - Paths to training and validation image directories
    - Number of classes (nc)
    - Class names
    
    Args:
        dataset_path (str): Path to the dataset directory where YAML file will be saved
        dataset_name (str): Name of the dataset (used for YAML filename)
    
    The resulting YAML file is saved as "{dataset_path}/{dataset_name}.yaml".
    """
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
    """
    Main function that orchestrates the dataset splitting process.
    
    Workflow:
    1. Parse command line arguments
    2. Set up paths for source dataset and output directories
    3. Create the output directory structure
    4. Get list of image subdirectories
    5. Split and copy images from source to train/val directories
    6. Copy corresponding label files for train/val images
    7. Generate YAML configuration file for YOLO training
    
    The resulting dataset will follow the standard YOLO directory structure
    with images and labels split according to the specified ratio.
    """
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
