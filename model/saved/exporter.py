"""
YOLO Model Exporter to TensorFlow Lite

This script exports a trained YOLO object detection model from PyTorch format
to TensorFlow Lite for deployment on mobile and edge devices.

Usage:
    python exporter.py --model cookie_v1.pt [OPTIONS]

Options:
    --model PATH         Path to the trained PyTorch model file (required)
    --imgsz WxH          Input image dimensions, format WxH (default: 640x480)
    --half               Enable float16 quantization
    --int8               Enable int8 quantization
    --data PATH          Path to dataset YAML file (required for int8 quantization)
    --output PATH        Output file path (default: derived from model name)
    --fraction           Fraction of data used for model export (default: 1.0)
    --device DEVICE      Device to run on, e.g. 'cpu' or '0' (default: auto-detect)

Examples:
    # Export with default settings
    python exporter.py --model cookie_v1.pt
    
    # Export with float16 quantization and custom size
    python exporter.py --model cookie_v1.pt --imgsz 320x320 --half
    
    # Export with int8 quantization
    python exporter.py --model cookie_v1.pt --int8 --data dataset.yaml
"""

import argparse
import os
from ultralytics import YOLO

def parse_args():
    """
    Parse command line arguments for the YOLO model exporter.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Export YOLO model to TensorFlow Lite")
    parser.add_argument("--model", type=str, required=True, help="Path to the trained PyTorch model file")
    parser.add_argument("--imgsz", type=str, default="640x480", help="Input image dimensions (WxH)")
    parser.add_argument("--half", action="store_true", help="Enable float16 quantization")
    parser.add_argument("--int8", action="store_true", help="Enable int8 quantization")
    parser.add_argument("--data", type=str, default=None, help="Path to dataset YAML (required for int8 quantization)")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--fraction", type=float, default=1.0, help="Fraction of data used for model export (default: 1.0)")
    parser.add_argument("--device", type=str, default="", help="Device to run on, e.g. 'cpu' or '0'")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.model):
        parser.error(f"Model file not found: {args.model}")
    
    if args.int8 and args.half:
        parser.error("--int8 and --half are mutually exclusive options")
    
    if args.int8 and not args.data:
        parser.error("--data is required when using --int8 quantization")
    
    if args.data and not os.path.exists(args.data):
        parser.error(f"Dataset file not found: {args.data}")
    
    # Parse image size
    try:
        width, height = map(int, args.imgsz.split("x"))
        args.imgsz = (height, width)  # YOLO uses (height, width) format
    except ValueError:
        parser.error("Image size must be in format WxH, e.g. 640x480")
    
    return args

def main():
    """
    Main function to export YOLO model to TensorFlow Lite format.
    """
    args = parse_args()
    
    print(f"Loading model from {args.model}")
    model = YOLO(args.model, task='detect')
    
    # Generate output filename if not specified
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.model))[0]
        quant_suffix = "_int8" if args.int8 else "_float16" if args.half else "_float32"
        args.output = f"{base_name}{quant_suffix}.tflite"
    
    print(f"Exporting model to {args.output}")
    print(f"Configuration: size={args.imgsz}, half={args.half}, int8={args.int8}, nms={args.nms}")
    
    # Export the model
    model.export(
        format='tflite',
        imgsz=args.imgsz,
        half=args.half,
        int8=args.int8,
        data=args.data,
        nms=args.nms,
        device=args.device,
        output=args.output
    )
    
    print(f"Model successfully exported to {args.output}")

if __name__ == "__main__":
    main()