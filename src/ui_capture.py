# ui_capture.py
import subprocess
import os
import argparse
import shutil

def run_ui_generator(app, width, height, widget_list, widget_count, output_file, delay_count, layout) -> None:
    subprocess.run([app, '-w', str(width), '-h', str(height), '-c', str(widget_count), '-t', ','.join(widget_list), '-o', output_file, '-d', str(delay_count), '-l', str(layout)])

def capture_ui(app: str, width: int, height: int, output_folder: str, iterations: int, widget_list: list, widget_count: int, delay_count: int, split_widgets: bool, layout: str) -> None:
    for i in range(iterations):
        #output_file = os.path.join(output_folder, f"ui_{i}.jpg")
        output_file_base = f"ui_{'-'.join(widget_list)}_{i}"
        output_file_image = f"{output_file_base}.jpg"
        output_file_text = f"{output_file_base}.txt"
        output_file_with_char = f"/{output_file_image}"
        
        #convert_binary_to_image(output_bin, width, height, image_output)
        if split_widgets:
            for widget in widget_list:
                output_file_base = f"ui_{widget}_{i}"
                output_file_image = f"{output_file_base}.jpg"
                output_file_text = f"{output_file_base}.txt"
                output_file_with_char = f"/{output_file_image}"
                run_ui_generator(app, width, height, [widget], widget_count, output_file_with_char, delay_count, layout)
                shutil.move(output_file_image, os.path.join(output_folder, widget, output_file_image))
                shutil.move(output_file_text, os.path.join(output_folder, widget, output_file_text))
        else:
            run_ui_generator(app, width, height, widget_list, widget_count, output_file_with_char, delay_count, layout)
            shutil.move(output_file_image, os.path.join(output_folder, output_file_image))
            shutil.move(output_file_text, os.path.join(output_folder, output_file_text))

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
    group = parser.add_mutually_exclusive_group(required=True)
    # Add boolean switch A
    group.add_argument('-s', '--single', action='store_true', help='Create only a single widget per iteration')

    # Add boolean switch B with additional parameter
    group.add_argument('-m', '--multi', action='store', type=int, help='Create multiple widgets per iteration')

    args = parser.parse_args()

    print(args)

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
            args.layout
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
            args.layout
        )