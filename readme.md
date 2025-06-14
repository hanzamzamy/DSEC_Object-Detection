# Oreo Cookie Detection with Synthetic Data

This project showcases a complete computer vision pipeline for detecting Oreo cookies using synthetic data generation, YOLO training, and AR deployment on Android.

## 🔍 Project Overview

This repository demonstrates an end-to-end workflow for object detection:

1. **Synthetic Data Generation**: Using Blender to create perfectly annotated training data
2. **Dataset Preparation**: Processing synthetic data into YOLO-compatible format
3. **Model Training**: Training YOLOv11 models on the synthetic dataset
4. **Android Deployment**: Implementing the trained model in an AR application

The project highlights how synthetic data can effectively train robust object detection models without manual data collection or annotation.

## 📁 Repository Structure

```
DSEC_Object-Detection/
├── blender/              # Synthetic data generation
├── dataset/              # Dataset preparation
├── model/                # Model training & export
└── android/              # AR implementation in Android devices
```

## ✨ Key Features

- **Synthetic Data Generation**: Create unlimited training examples with perfect annotations
- **Comprehensive Training Pipeline**: From data preparation to model evaluation
- **TensorFlow Lite Export**: Optimized models for mobile deployment
- **AR Integration**: Real-time detection with AR object placement
- **Interactive 3D Avatar**: Character that interacts with detected objects

## 📊 Workflow

### 1. Synthetic Data Generation (Blender)

The project uses Blender to generate synthetic training data with automatic annotations:

- 3D models of Oreo cookies placed in varied positions/orientations
- Randomized lighting, backgrounds, and textures
- Automatic generation of bounding box annotations
- Support for different annotation formats (vertices, cuboids)

More details on synthetic data ![section](/blender).

### 2. Dataset Preparation

The synthetic data is processed into a format suitable for YOLO training:

- Organization into train/validation splits
- Label recycling mechanism for efficiency
- Generation of YOLO-compatible configuration files
- Verification tools to ensure data quality

More details on dataset ![section](/dataset).

### 3. Model Training

YOLOv11 models are trained on the prepared synthetic dataset:

- Training on Kaggle with 2×T4 GPUs
- Comprehensive evaluation metrics and visualizations
- Model export to TensorFlow Lite for mobile deployment
- Inference testing on sample videos

More details on model ![section](/model).

### 4. Android AR Implementation

The trained model is deployed in an Android AR application:

- Real-time Oreo cookie detection using TensorFlow Lite
- AR object placement at detected locations
- Interactive 3D avatar that navigates to detected objects
- Modern UI with Jetpack Compose and Material3

More details on Android implementation ![section](/android).

## 🔧 Getting Started

### Prerequisites

- Blender 3.0+ (for synthetic data generation)
- Python 3.8+ with PyTorch, TensorFlow, and Ultralytics
- Android Studio / Intellij Idea (Android app development)
- AR Core compatible Android device

## 📊 Results

The model achieved high performance metrics despite being trained exclusively on synthetic data:

- **mAP50**: 0.995
- **Precision**: 0.999
- **Recall**: 0.992

These results validate the synthetic data approach, showing excellent performance even on real-world test cases.

## 📱 Android AR Demo

The Android application provides an immersive AR experience with real-time object detection:

1. Point your camera at Oreo cookies
2. Virtual indicators are placed at detection locations
3. Control the 3D avatar to interact with detected objects
4. Explore AR space with intuitive controls

## 📎 Resources

- [Dataset on Kaggle](https://www.kaggle.com/datasets/rayhanzamzamy/oreo-cookie-detection)
- [Training Notebook on Kaggle](https://www.kaggle.com/code/rayhanzamzamy/dsec-oreo-cookie-detect)

## 🔗 Related Projects

- [YOLOv11](https://github.com/ultralytics/ultralytics) - You Only Look Once version 11
- [SceneView](https://github.com/SceneView/sceneview-android) - AR framework for Android

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgements

- [Nexon Games](https://www.nexon.com/) - For the character from [Blue Archive](https://bluearchive.nexon.com/) used in the AR implementation
