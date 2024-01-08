# ui_capture.py
import subprocess
import os
import argparse
import shutil
import random

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

def run_ui_generator(app, width, height, widget_list, widget_count, output_file, delay_count, layout) -> None:
    subprocess.run([app, '-w', str(width), '-h', str(height), '-c', str(widget_count), '-t', ','.join(widget_list), '-o', output_file, '-d', str(delay_count), '-l', str(layout)])

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

def data_file_generation(output_folder, images, split_ratio=(0.7, 0.1, 0.2), class_names: list = None, replace: tuple = None):
    # Assume split_ratio is a tuple of three numbers (train, val, test) that sums to 1
    random.shuffle(images)
    num_train = int(len(images) * split_ratio[0])
    num_val = int(len(images) * split_ratio[1])

    train_images = images[:num_train]
    val_images = images[num_train:num_train + num_val]
    test_images = images[num_train + num_val:]

    # Assuming classes.names file is in the output_folder
    num_classes = sum(1 for line in open(os.path.join(output_folder, 'classes.names')))

    train_file = os.path.join(output_folder, 'train.txt')
    val_file = os.path.join(output_folder, 'val.txt')
    test_file = os.path.join(output_folder, 'test.txt')
    names_file = os.path.join(output_folder, 'classes.names')

    train_folder = os.path.join(output_folder, 'train')
    val_folder = os.path.join(output_folder, 'val')
    test_folder = os.path.join(output_folder, 'test')

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    for i, image_path in enumerate(train_images):
        new_image_path = os.path.join(train_folder, os.path.basename(image_path))
        shutil.move(image_path, new_image_path)
        train_images[i] = new_image_path
        label_path = image_path.replace('.jpg', '.txt')
        new_label_path = os.path.join(train_folder, os.path.basename(label_path))
        shutil.move(label_path, new_label_path)

    for i, image_path in enumerate(val_images):
        new_image_path = os.path.join(val_folder, os.path.basename(image_path))
        shutil.move(image_path, new_image_path)
        val_images[i] = new_image_path
        label_path = image_path.replace('.jpg', '.txt')
        new_label_path = os.path.join(val_folder, os.path.basename(label_path))
        shutil.move(label_path, new_label_path)

    for i, image_path in enumerate(test_images):
        new_image_path = os.path.join(test_folder, os.path.basename(image_path))
        shutil.move(image_path, new_image_path)
        test_images[i] = new_image_path
        label_path = image_path.replace('.jpg', '.txt')
        new_label_path = os.path.join(test_folder, os.path.basename(label_path))
        shutil.move(label_path, new_label_path)

    create_dataset_list_file(train_images, train_file, replace=replace)
    create_dataset_list_file(val_images, val_file, replace=replace)
    create_dataset_list_file(test_images, test_file, replace=replace)
    if replace is not None:
        train_file = train_file.replace(replace[old], replace[new])
        val_file = val_file.replace(replace[old], replace[new])
        test_file = test_file.replace(replace[old], replace[new])
        names_file = names_file.replace(replace[old], replace[new])
    create_data_file(output_folder, num_classes, train_file, val_file, names_file)

def replace_class_by_index(yolo_file: str, class_name: str, index: int) -> None:
    with open(yolo_file, 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith(class_name):
                # Replace the class name with the index: "lv_btn ..." -> "0 ..."
                lines[i] = f"{index}{line[len(class_name):]}"
        file.seek(0)
        file.writelines(lines)
        file.truncate()

def capture_ui(app: str, width: int, height: int, output_folder: str, iterations: int, widget_list: list, widget_count: int, delay_count: int, split_widgets: bool, layout: str, replace: tuple = None) -> None:
    image_paths = []
    for i in range(iterations):
        output_file_base = f"ui_{'-'.join(widget_list)}_{i}"
        output_file_image = f"{output_file_base}.jpg"
        output_file_text = f"{output_file_base}.txt"
        output_file_with_char = f"/{output_file_image}"
        os.makedirs(output_folder, exist_ok=True)
        if split_widgets:
            for widget in widget_list:
                output_file_base = f"ui_{widget}_{i}"
                output_file_image = f"{output_file_base}.jpg"
                output_file_text = f"{output_file_base}.txt"
                output_file_with_char = f"/{output_file_image}"
                output_image_path = os.path.join(output_folder, output_file_image)
                output_text_path = os.path.join(output_folder, output_file_text)
                run_ui_generator(app, width, height, [widget], widget_count, output_file_with_char, delay_count, layout)
                shutil.move(output_file_image, output_image_path)
                shutil.move(output_file_text, os.path.join(output_folder, output_file_text))
                replace_class_by_index(output_text_path, classes[widget]['name'], classes[widget]['index'])
                image_paths.append(output_image_path)
        else:
            output_image_path = os.path.join(output_folder, output_file_image)
            run_ui_generator(app, width, height, widget_list, widget_count, output_file_with_char, delay_count, layout)
            shutil.move(output_file_image, output_image_path)
            shutil.move(output_file_text, os.path.join(output_folder, output_file_text))
            replace_class_by_index(output_text_path, classes[widget]['name'], classes[widget]['index'])
            image_paths.append(output_image_path)
    # Get sublist of real widget names from the classes dictionary
    class_names = [classes[widget]['name'] for widget in widget_list]
    with open(os.path.join(output_folder, 'classes.names'), 'w') as file:
        for class_n in class_names:
            file.write(f"{class_n}\n")
    data_file_generation(output_folder, image_paths, class_names=class_names, replace=replace)

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
    parser.add_argument('--layout', type=str, required=True, help='Layout of the UI')
    parser.add_argument('-r', '--replace', type=str, nargs='+', default=None, help='Replace all paths with the given tuple (old, new) for data usage in different environment')
    group = parser.add_mutually_exclusive_group(required=True)
    # Add boolean switch A
    group.add_argument('-s', '--single', action='store_true', help='Create only a single widget per iteration')

    # Add boolean switch B with additional parameter
    group.add_argument('-m', '--multi', action='store', type=int, help='Create multiple widgets per iteration')

    args = parser.parse_args()

    print(args)
    if args.replace is not None:
        if len(args.replace) != 2:
            print("Replace argument must be a tuple of two strings (old, new)")
            exit(1)
        args.replace = tuple(args.replace)

    # Check if widget types are valid
    for widget in args.widget_types:
        if widget not in classes.keys():
            print(f"Widget type {widget} not supported. Please use one of the following: {', '.join(classes.keys())}")
            exit(1)

    if args.single:
        capture_ui(
            os.path.abspath(args.app_path),
            args.width,
            args.height,
            os.path.abspath(args.output_folder),
            args.iterations,
            args.widget_types,
            1,
            args.delay_count,
            args.split_widgets,
            args.layout,
            args.replace
        )
    elif args.multi is not None:
        capture_ui(
            os.path.abspath(args.app_path),
            args.width,
            args.height,
            os.path.abspath(args.output_folder),
            args.iterations,
            args.widget_types,
            args.multi,
            args.delay_count,
            args.split_widgets,
            args.layout,
            args.replace
        )