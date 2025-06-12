from ultralytics import YOLO

modelPath = 'cookie_v1.pt'

imageSize = (480,640)

# Model quantization, mutually exclusive
enable_f16 = False
enable_int8 = False
datasetPath = '../dataset/split/ore_cookie/oreo_cookie.yaml' # int8 quantization need dataset for calibration

model = YOLO(modelPath)
model.export(format='tflite', imgsz=imageSize, half=enable_f16, int8=enable_int8, data=datasetPath)
