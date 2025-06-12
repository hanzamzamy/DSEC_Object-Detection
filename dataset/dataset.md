# Dataset Preparation for YOLO Training

This section explains how the synthetic data generated in Blender is processed into a format suitable for training YOLO object detection models.

## Initial Data Structure

The synthetic data is initially organized as follows:
```
<dataset_name>/
├── images/
│   ├── <image_subset_1>/
│   ├── ...
│   └── <image_subset_n>/
├── labels/
    ├── <label_type_1>/
    ├── ...
    └── <label_type_n>/
```

Each image subset contains variations of the same object with different backgrounds, lighting conditions, and effects. Since the 3D object positioning remains identical across these variations, the annotation data can be reused across different image variants.

## Label Recycling Mechanism

One of the key advantages of using synthetic data is the ability to reuse annotations. Since the object positions and camera angles are identical across different rendering environments (backgrounds, lighting, etc.), we can recycle the annotation files:

1. The image files in each subset follow a common naming pattern (e.g., `1.jpg`, `2.jpg`)
2. The corresponding label files use the same numbering system (`1.txt`, `2.txt`)
3. When processing the dataset, we match images to labels based on this numbering system

This approach significantly reduces the annotation workload and ensures perfect consistency across the dataset.

## Dataset Splitting Process

The `splt.py` script handles the dataset preparation as follow:

1. **Dataset Configuration**:
   - Source dataset path
   - Output dataset name
   - Train/validation split ratio (default: 80% train, 20% validation)
   - Label type to use (e.g., `label_vertice`, `label_cuboid`)

2. **Directory Creation**:
   - Creates the standard YOLO directory structure:
     ```
     <dataset_name>/
     ├── train/
     │   ├── images/
     │   └── labels/
     ├── val/
     │   ├── images/
     │   └── labels/
     └── <dataset_name>.yaml
     ```

3. **Image Splitting**:
   - For each image subset folder:
     - List all images and shuffle them randomly
     - Split according to the specified ratio
     - Copy to train/val image folders with modified names that preserve their source subset

4. **Label Processing**:
   - For each image in the train/val directories:
     - Extract the original image ID from the filename
     - Look up the corresponding label file
     - For background images (prefixed with "BG_"), use a special "bg.txt" label
     - Copy the label file to the appropriate destination with a matching filename

5. **YAML Generation**:
   - Creates a YAML configuration file required by YOLO with:
     - Paths to training and validation data
     - Number of classes (1 - just "cookie")
     - Class names

## Verification

The repository also includes a `check.py` script to visualize the prepared dataset:

- Reads images and corresponding labels
- Draws bounding boxes around detected objects
- Highlights keypoints if present in the annotation
- Saves the visualized images to a result directory

This allows for quick verification that the dataset splitting process worked correctly and that all annotations are properly aligned with their images.

## Usage Example

```bash
# Split dataset with default 80/20 ratio
python splt.py --datasource_path ./raw/cookie --dataset_name oreo_cookie --label_type label_vertice

# Visualize the prepared dataset
python check.py --dataset oreo_cookie --outdir ./quality_check/cookie
```

By following this process, the synthetic data generated in Blender is transformed into a clean, properly structured dataset ready for training YOLO object detection models.