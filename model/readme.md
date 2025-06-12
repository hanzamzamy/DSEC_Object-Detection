# Model Training and Deployment

This section covers the complete workflow of YOLO-based object detection system for Oreo cookies, from training through deployment to inference testing.

## Model Training

### Training Environment

The model was trained on Kaggle's accelerated computing environment using 2 × T4 GPU resources:

- **Notebook**: [DSEC Oreo Cookie Detect on Kaggle](https://www.kaggle.com/code/rayhanzamzamy/dsec-oreo-cookie-detect)
- **Hardware**: 2 × NVIDIA T4 GPU
- **Framework**: Ultralytics YOLO v11

### Training Configuration

`trainval/oreo-cookie-train.ipynb` notebook implements the training & validation pipeline. Key training hyperparameters (from `trainval/v1/args.yaml`)

## Validation and Metrics

After training, the model achieved strong performance on the synthetic dataset:

| Metric | Value |
|--------|-------|
| mAP50 | 0.995 |
| Precision | 0.999 |
| Recall | 0.992 |

### Visualization and Analysis

The training process generated extensive visualization artifacts in `trainval/v1/`:

- **Precision-Recall Curves**: `PR_curve.png`, `P_curve.png`, `R_curve.png`
- **F1 Score Analysis**: `F1_curve.png`
- **Confusion Matrix**: `confusion_matrix.png`, `confusion_matrix_normalized.png`
- **Label Distribution**: `labels.jpg`, `labels_correlogram.jpg`
- **Batch Previews**: 
  - Training: `train_batch0.jpg`
  - Validation: `val_batch0_labels.jpg`, `val_batch0_pred.jpg`

These visualizations helped verify the model's performance across different viewing angles and backgrounds, confirming that synthetic data generation approach provided effective training material.

## Model Export

The trained PyTorch model was exported to TensorFlow Lite format using the `saved/exporter.py` script:

### Export Options

The script supports various export configurations:

- **Float32 model**: Default full-precision model
- **Float16 model**: Half-precision model
- **Int8 quantization**: For improved performance on mobile devices. Require data for calibration.

## Inference Testing

The exported model was tested using the `inference/test_detection.py` script on sample videos:

- `dummy_oreo.mkv`: Standard orientation test
- `dummy_oreo-rotated.mkv`: Rotated orientation test

The testing script evaluates:
- Detection accuracy
- Processing speed (FPS)
- Handling of various orientations and lighting conditions

Example inference command:
```bash
python inference/test_detection.py --weights saved/cookie_v1.pt --source inference/dummy_oreo.mkv
```

## Android Integration

The TensorFlow Lite model (`cookie_v1_float32.tflite`) was integrated into our Android application using TFLite's Android libraries, as described in the Android section of this repository.

## Performance Summary

- **Model Size**: ~5MB (saved weight), ~10MB (TFLite Float32).
- **Inference Time**: TFLite (25-45ms) on PC, takes longer on Android device (mid-range specification).
- **Accuracy**: > 85%

Synthetic data approach proved highly effective, with the model showing robust performance even on real-world images despite being trained exclusively on synthetic data.