# ui_capture.py
import subprocess
import os
import argparse
import shutil
import random
import yaml

from typing import List
from typing import Tuple

from util import replace
from util import generators
from util import normalize
from util import yolo_to_coco

default_widget_list = ['button', 'checkbox', 'label', 'slider', 'switch', 'progressbar']
# Some constants
old = 0
new = 1
classes = {
    "button": {"name": "lv_btn", "index": 0},
    "checkbox": {"name": "lv_checkbox", "index": 1},
    "label": {"name": "lv_label", "index": 2},
    "slider": {"name": "lv_slider", "index": 3},
    "switch": {"name": "lv_switch", "index": 4},
    "progressbar": {"name": "lv_bar", "index": 5},
}

def run_ui_generator(app: str, out_dir: str, 
                     width: int, height: int, widget_list: int, widget_count: int, output_file: int, delay_count: int, 
                     layout: str = None) -> None:
    """
    Run the random UI generator binary with the provided parameters

    app: path to the random UI generator binary
    out_dir: path to the output folder
    width: width of the UI screenshot
    height: height of the UI screenshot
    widget_list: list of widgets to be used in the UI
    widget_count: number of widgets to be used in the UI
    output_file: path to the output file
    delay_count: amount of times the timer handler shall be called with a fixed delay before capturing the UI (amount is multiplied by 1000ms in the binary)
    layout: layout to be used in the UI (none, grid, flex)
    """
    if layout is None:
        subprocess.run(executable=app, cwd=out_dir, args=[app, '-w', str(width), '-h', str(height), '-c', str(widget_count), '-t', ','.join(widget_list), '-o', output_file, '-d', str(delay_count), '-l', 'none'])
    else:
        subprocess.run(executable=app, cwd=out_dir, args=[app, '-w', str(width), '-h', str(height), '-c', str(widget_count), '-t', ','.join(widget_list), '-o', output_file, '-d', str(delay_count), '-l', str(layout)])

def create_dataset(root: str, images: List[str], labels: List[str], output_folder: str) -> None:
    os.makedirs(output_folder, exist_ok=True)
    for image_path in images:
        shutil.move(image_path, os.path.join(output_folder, 'images', os.path.basename(image_path)))
    for label_path in labels:
        shutil.move(label_path, os.path.join(output_folder, 'labels', os.path.basename(label_path)))
    # if replace is not None:
    #     output_folder = output_folder.replace(replace[old], replace[new])
    # replace.replace_paths_in_dataset_files(output_folder, replace)

def create_data_file(data_folder, num_classes, train_file, val_file, names_file):
    data_file_path = os.path.join(data_folder, 'custom.data')
    with open(data_file_path, 'w') as file:
        file.write(f"classes={num_classes}\n")
        file.write(f"train={train_file}\n")
        file.write(f"valid={val_file}\n")
        file.write(f"names={names_file}\n")
    return data_file_path

def create_dataset_list_file(file_paths, output_file, replace: tuple = None):
    with open(output_file, 'w') as file:
        for path in file_paths:
            if replace is not None:
                path = path.replace(replace[old], replace[new])
            file.write(path + '\n')

def create_dataset_yaml_file(output_folder: str, name: str, classes: str, train_dir: str, val_dir: str, test_dir: str = None) -> dict:
    """
    Create a yaml file for the dataset using the provided name, classes and directories

    Example dataset.yaml file:
    # Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]
    path: ../datasets/coco8  # dataset root dir
    train: images/train  # train images (relative to 'path') 4 images
    val: images/val  # val images (relative to 'path') 4 images
    test:  # test images (optional)

    # Classes (80 COCO classes)
    names:
      0: person
      1: bicycle
      2: car
      # ...
      77: teddy bear
      78: hair drier
      79: toothbrush
    """
    classes_dict = {}
    for i, class_name in enumerate(classes):
        classes_dict[i] = class_name
    dataset_yaml = {
        'path': output_folder,
        'train': train_dir,
        'val': val_dir,
        'test': test_dir,
        'names': classes_dict
    }
    with open(os.path.join(output_folder, f"{name}.yaml"), 'w') as file:
        yaml.dump(dataset_yaml, file)
    return classes_dict


def move_image_file_with_label(image_path: str, image_output_dir: str, label_output_dir) -> str:
    new_image_path = os.path.join(image_output_dir, os.path.basename(image_path))
    shutil.move(image_path, new_image_path)
    label_path = image_path.replace('.jpg', '.txt')
    shutil.move(label_path, os.path.join(label_output_dir, os.path.basename(label_path)))
    return new_image_path

def shuffle_image_files(image_files: List[str], split_ratio: tuple = (0.7, 0.1, 0.2)) -> Tuple[List[str], List[str], List[str]]:
    # Assume split_ratio is a tuple of three numbers (train, val, test) that sums to 1
    random.shuffle(image_files)
    num_train = int(len(image_files) * split_ratio[0])
    num_val = int(len(image_files) * split_ratio[1])

    train_images = image_files[:num_train]
    val_images = image_files[num_train:num_train + num_val]
    test_images = image_files[num_train + num_val:]

    return (train_images, val_images, test_images)

def dataset_generation(output_folder: str, name: str, images: List[str], width: int, height: int, class_names: List[str], split_ratio: tuple = None):
    """
    Generate a dataset from a list of images
    """
    # Some variables
    train_img_dir = "images/train"
    train_label_dir = "labels/train"
    val_img_dir = "images/val"
    val_label_dir = "labels/val"
    test_img_dir = "images/test"
    test_label_dir = "labels/test"
    target_dir = os.path.join(output_folder, name)
    train_img_folder = os.path.join(target_dir, train_img_dir)
    train_label_folder = os.path.join(target_dir, train_label_dir)
    val_img_folder = os.path.join(target_dir, val_img_dir)
    val_label_folder = os.path.join(target_dir, val_label_dir)
    test_img_folder = os.path.join(target_dir, test_img_dir)
    test_label_folder = os.path.join(target_dir, test_label_dir)

    # Create all necessary folders
    folders = [target_dir, train_img_folder, train_label_folder, val_img_folder, val_label_folder, test_img_folder, test_label_folder]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Shuffle images
    if split_ratio is None:
        train_images, val_images, test_images = shuffle_image_files(images)
    else:
        train_images, val_images, test_images = shuffle_image_files(images, split_ratio)
    # FIXME images and labels aren't moved properly!
    # Move all images and labels to the correct folders
    for i, image_path in enumerate(train_images):
        train_images[i] = move_image_file_with_label(image_path, train_img_folder, train_label_folder)
    for i, image_path in enumerate(val_images):
        val_images[i] = move_image_file_with_label(image_path, val_img_folder, val_label_folder)
    for i, image_path in enumerate(test_images):
        test_images[i] = move_image_file_with_label(image_path, test_img_folder, test_label_folder)

    # Dictionary in the format: {class_id: class_name}
    class_dict = create_dataset_yaml_file(target_dir, name, class_names, train_img_dir, val_img_dir, test_img_dir)

    # Fix label files to use class_id instead of class_name
    for label_file in generators.annotation_files_in_dirs([train_label_folder, val_label_folder, test_label_folder]):
        replace.replace_class_names_with_id_in_file(class_names, label_file)
        normalize.normalize_bbox_in_label_file(label_file, width, height)

def capture_ui(app: str, output_folder: str,
               width: int, height: int, iterations: int, 
               widget_list: list, widget_count: int, delay_count: int, split_widgets: bool, 
               split_ratio: tuple = None,
               dataset_name: str = 'custom', layout: str = None) -> None:
    image_paths = []
    os.makedirs(output_folder, exist_ok=True)
    for i in range(iterations):
        output_file_base = f"ui_{'-'.join(widget_list)}_{i}"
        output_file_image = f"{output_file_base}.jpg"
        output_file_with_char = f"/{output_file_image}"
        if split_widgets:
            for widget in widget_list:
                output_file_base = f"ui_{widget}_{i}"
                output_file_image = f"{output_file_base}.jpg"
                output_file_with_char = f"/{output_file_image}"
                output_image_path = os.path.join(output_folder, output_file_image)
                run_ui_generator(app, output_folder, width, height, [widget], widget_count, output_file_with_char, delay_count, layout)
                image_paths.append(output_image_path)
        else:
            output_image_path = os.path.join(output_folder, output_file_image)
            run_ui_generator(app, output_folder, width, height, widget_list, widget_count, output_file_with_char, delay_count, layout)
            image_paths.append(output_image_path)
    # Get new list of real widget names from the classes dictionary
    class_names = [classes[widget]['name'] for widget in widget_list]
    dataset_generation(output_folder=output_folder, name=dataset_name, images=image_paths, width=width, height=height, class_names=class_names, split_ratio=split_ratio)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture UI and create image and annotation with correct folders.')
    parser.add_argument('-p', '--app_path', required=True, help='Path to the random UI generator binary')
    parser.add_argument('-i', '--iterations', type=int, default=10, help='Number of UIs to generate')
    parser.add_argument('-t','--widget_types', required=True, nargs='+', help='List of widgets to be used in the UI')
    parser.add_argument('--width', type=int, default=250, help='Width of the UI screenshot')
    parser.add_argument('--height', type=int, default=250, help='Height of the UI screenshot')
    parser.add_argument('-o','--output_folder', required=True, help='Folder to save the output images')
    parser.add_argument('-d','--delay_count', type=int, default=10, help='Amount of times the timer handler shall be called with a fixed delay before capturing the UI')
    parser.add_argument('--split_widgets', action='store_true', help='Split widgets into subfolders (only creates one widget type per iteration)')
    parser.add_argument('-l', '--layout', type=str, default=None, help='Path to the layout file to be used')
    parser.add_argument('-r', '--split_ratio', type=str, default=None, help='Split ratio for train, val, test')
    group = parser.add_mutually_exclusive_group(required=True)
    # Add boolean switch A
    group.add_argument('-s', '--single', action='store_true', help='Create only a single widget per iteration')

    # Add boolean switch B with additional parameter
    group.add_argument('-m', '--multi', action='store', type=int, help='Create multiple widgets per iteration')

    args = parser.parse_args()

    print(args)

    # Check if widget types are valid
    for widget in args.widget_types:
        if widget not in classes.keys():
            print(f"Widget type {widget} not supported. Please use one of the following: {', '.join(classes.keys())}")
            exit(1)

    if args.single:
        capture_ui(
            app=os.path.abspath(args.app_path),
            output_folder=os.path.abspath(args.output_folder),
            width=args.width,
            height=args.height,
            iterations=args.iterations,
            widget_list=args.widget_types,
            widget_count=1,
            delay_count=args.delay_count,
            split_widgets=args.split_widgets,
            split_ratio=args.split_ratio,
            layout=args.layout
        )
    elif args.multi is not None:
        capture_ui(
            app=os.path.abspath(args.app_path),
            output_folder=os.path.abspath(args.output_folder),
            width=args.width,
            height=args.height,
            iterations=args.iterations,
            widget_list=args.widget_types,
            widget_count=args.multi,
            delay_count=args.delay_count,
            split_widgets=args.split_widgets,
            split_ratio=args.split_ratio,
            layout=args.layout
        )