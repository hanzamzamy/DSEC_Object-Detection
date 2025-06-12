# Synthetic Data Generation for Oreo Cookie Detection

Instead of collecting and manually labeling real-world data, this project uses Blender to generate synthetic training data with automatic, pixel-perfect annotations.

## Overview

The pipeline consists of:
1. 3D model creation/import into Blender.
2. Blender file that implement semi-realistic effect, such as shading/lighting, material, texture, etc.
3. Synthetic data generation with automated annotation script.

## Blender Scripts

### annotate_n_render.py

This is the main script for generating synthetic data with annotations. It provides:

- **Automatic Annotation**: Converts 3D object coordinates to 2D bounding boxes in YOLO format (`<class> <cx> <cy> <w> <h>`)
- **Random Lighting**: Creates and animates multiple point lights with random colors, positions, and intensities
- **Background Variation**: Generates diverse backgrounds with configurable patterns:
  - Solid colors
  - Noise textures
  - Voronoi patterns
  - Grid patterns
- **Batch Processing**: Processes multiple frames with different configurations

### animate_random_in_cam.py

This script places Oreo cookie objects randomly within the camera frame:

- Creates random positions and orientations for objects
- Ensures objects remain within camera view
- Generates keyframes for animation
- Controls placement with parameters like `position_range` and `bounds_margin` to maintain visibility

### animate_fibonacci_sphere.py

This script creates comprehensive viewing angle coverage:

- Uses Fibonacci sphere distribution for even sampling of viewing directions
- Rotates the object to cover all possible orientations (evenly distributed)
- Creates smooth animations by adding spin at each position
- Generates `n_pitch * n_spin` total frames (2000 in the example)

## Advantages of Synthetic Data Generation

1. **Perfect Annotations**: Annotations are mathematically derived from the 3D scene, eliminating human error
2. **Infinite Variation**: Generate unlimited training examples with different lighting, backgrounds, positions
3. **Time Efficiency**: Avoids time-consuming manual labeling
4. **Edge Case Coverage**: Can systematically generate difficult scenarios