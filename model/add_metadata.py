from tflite_support.metadata_writers import writer_utils
from tflite_support.metadata_writers import object_detector
# from tflite_support.metadata_schema_py_generated import ScoreCalibrationType

# Paths
MODEL_PATH = "cookie_v1.tflite"
OUTPUT_PATH = "cookie_v1_meta.tflite"

# Dummy labels file — optional
with open("labels.txt", "w") as f:
    f.write("object\n")

# Create metadata writer
writer = object_detector.MetadataWriter.create_for_inference(
    writer_utils.load_file(MODEL_PATH),
    input_norm_mean=[0.0],   # YOLO uses img / 255.0
    input_norm_std=[255.0],
    label_file_paths=["labels.txt"]
)

# Write model with metadata
writer_utils.save_file(writer.populate(), OUTPUT_PATH)

print("✅ Metadata written to:", OUTPUT_PATH)
