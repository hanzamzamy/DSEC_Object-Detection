import os
import argparse

def change_class_id(dataset_name, target_class_id, output_dir):
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
                    if len(parts) >= 1:
                        parts[0] = str(target_class_id)
                        outfile.write(" ".join(parts) + '\n')

    print(f"Updated labels with class ID = {target_class_id} saved to: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Change class ID in YOLO label files.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name (e.g., 'output')")
    parser.add_argument("--classid", type=int, required=True, help="Target class ID to set (e.g., 0)")
    parser.add_argument("--outdir", type=str, default="./updated_class", help="Output directory for modified labels")
    args = parser.parse_args()

    change_class_id(args.dataset, args.classid, args.outdir)
