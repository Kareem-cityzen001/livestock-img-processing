"""
Convert Roboflow export (classification or detection/YOLO) into a classification
folder layout that `better_train.py` expects, then launch training.

Usage:
  python convert_and_train.py /path/to/dataset.zip
  OR
  python convert_and_train.py /path/to/extracted_dataset_folder

The script will create (or replace) `c:/TROJAN/datasets/train` with class folders.
"""
import sys
import os
import zipfile
import shutil
import tempfile
from pathlib import Path
import yaml
import subprocess

WORKDIR = Path("c:/TROJAN")
TARGET = WORKDIR / "datasets" / "train"


def extract_zip(zip_path, dest):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(dest)


def find_data_yaml(root):
    for p in root.rglob('data.yaml'):
        return p
    return None


def parse_yaml(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def convert_detection_to_classification(root, out_folder):
    """Handle Roboflow YOLO-style layout: train/images, train/labels, valid, test
    Use data.yaml names to map class indices to class names.
    """
    data_yaml = find_data_yaml(root)
    if data_yaml is None:
        raise RuntimeError("Could not find data.yaml to map class ids to names")
    meta = parse_yaml(data_yaml)
    names = meta.get('names') or meta.get('nc_names') or meta.get('class_names')
    if isinstance(names, dict):
        # sometimes names are dict mapping idx->name
        name_list = [names[str(i)] for i in range(len(names))]
    else:
        name_list = list(names)

    # create class folders
    shutil.rmtree(out_folder, ignore_errors=True)
    out_folder.mkdir(parents=True, exist_ok=True)
    for nm in name_list:
        (out_folder / nm).mkdir(parents=True, exist_ok=True)

    # collect all images under any */images folders and their corresponding labels
    images = list(root.rglob('images/*'))
    images = [p for p in images if p.is_file() and p.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    if not images:
        raise RuntimeError('No images found in dataset images/* folders')

    for img in images:
        rel = img.relative_to(root)
        # try to find corresponding label file in same folder under ../labels
        label_file = img.with_suffix('.txt').with_name(img.stem + '.txt')
        # Roboflow often places label txt in parallel folder ../labels
        label_candidate = img.parent.parent / 'labels' / img.name.replace(img.suffix, '.txt')
        label_paths = [label_file, label_candidate]
        label_path = None
        for lp in label_paths:
            if lp.exists():
                label_path = lp
                break
        assigned = False
        if label_path:
            # read labels, choose first class id as label
            with open(label_path, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if lines:
                first = lines[0].split()[0]
                try:
                    idx = int(first)
                    class_name = name_list[idx]
                except Exception:
                    class_name = name_list[0]
                dest = out_folder / class_name / img.name
                shutil.copy2(img, dest)
                assigned = True
        if not assigned:
            # No label file; place into a folder named "unlabeled"
            (out_folder / 'unlabeled').mkdir(exist_ok=True)
            shutil.copy2(img, out_folder / 'unlabeled' / img.name)

    # remove unlabeled folder if empty
    unl = out_folder / 'unlabeled'
    if unl.exists() and not any(unl.iterdir()):
        unl.rmdir()

    # report counts
    counts = {d.name: len(list((out_folder/d.name).glob('*'))) for d in out_folder.iterdir() if d.is_dir()}
    return counts


def convert_classification_to_target(root, out_folder):
    # root should already have class subfolders
    shutil.rmtree(out_folder, ignore_errors=True)
    out_folder.mkdir(parents=True, exist_ok=True)
    for sub in root.iterdir():
        if sub.is_dir():
            dest = out_folder / sub.name
            shutil.copytree(sub, dest)
    counts = {d.name: len(list((out_folder/d.name).glob('*'))) for d in out_folder.iterdir() if d.is_dir()}
    return counts


def main():
    if len(sys.argv) < 2:
        print('Usage: python convert_and_train.py <path-to-zip-or-folder>')
        sys.exit(1)
    src = Path(sys.argv[1])
    if not src.exists():
        print('Path not found:', src)
        sys.exit(1)

    tmpdir = Path(tempfile.mkdtemp())
    work_root = tmpdir
    try:
        if src.is_file() and src.suffix.lower() == '.zip':
            print('Extracting', src, 'to', tmpdir)
            extract_zip(src, tmpdir)
            # try to find a top-level extracted folder
            children = list(tmpdir.iterdir())
            if len(children) == 1 and children[0].is_dir():
                work_root = children[0]
        elif src.is_dir():
            work_root = src
        else:
            print('Unsupported input')
            sys.exit(1)

        # Decide if classification formatted (folders per class) or detection (train/images/...)
        has_class_folders = any((p for p in work_root.iterdir() if p.is_dir() and any(p.glob('*.*'))))
        # more robust detection check
        if (work_root / 'train').exists() and (work_root / 'train' / 'images').exists():
            print('Detected Roboflow detection layout; converting to classification...')
            counts = convert_detection_to_classification(work_root, TARGET)
        else:
            print('Detected classification layout or simple folders; copying to target...')
            counts = convert_classification_to_target(work_root, TARGET)

        print('\nDataset conversion complete. Class counts:')
        for k,v in counts.items():
            print(f'  {k}: {v}')

        # minimal sanity checks
        total = sum(counts.values())
        if total < 20:
            print('\nWARNING: Dataset is small (<20 images). Training may not generalize.')

        # Start training using workspace venv python and better_train.py
        venv_py = Path('C:/TROJAN/.venv/Scripts/python.exe')
        if not venv_py.exists():
            venv_py = shutil.which('python')
        cmd = [str(venv_py), 'better_train.py']
        print('\nStarting training:',' '.join(cmd))
        subprocess.run(cmd, cwd=str(WORKDIR))

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == '__main__':
    main()
