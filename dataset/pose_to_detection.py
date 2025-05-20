import os
import argparse

def convert_pose_to_detection(dataset_name, output_dir):
    label_dirs = [f"./{dataset_name}/train/labels", f"./{dataset_name}/val/labels"]
    output_dirs = [os.path.join(output_dir, "train", "labels"), os.path.join(output_dir, "val", "labels")]

    for in_dir, out_dir in zip(label_dirs, output_dirs):
        os.makedirs(out_dir, exist_ok=True)

        for file_name in os.listdir(in_dir):
            if not file_name.endswith(".txt"):
                continue

            in_path = os.path.join(in_dir, file_name)
            out_path = os.path.join(out_dir, file_name)

            with open(in_path, 'r') as infile:
                lines = infile.readlines()

            with open(out_path, 'w') as outfile:
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        detection_line = " ".join(parts[:5])
                        outfile.write(detection_line + '\n')

    print(f"Detection labels saved to: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert pose keypoint labels to detection labels.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name (e.g., 'output')")
    parser.add_argument("--outdir", type=str, default="./det_labels", help="Output directory for detection labels")
    args = parser.parse_args()

    convert_pose_to_detection(args.dataset, args.outdir)
