'''
File: ui_capture.py
Created on: Thursday, 1970-01-01 @ 01:00:00
Author: HackXIt (<hackxit@gmail.com>)
-----
Last Modified: Monday, 2023-11-20 @ 03:12:31
Modified By:  HackXIt (<hackxit@gmail.com>) @ HACKXIT
-----
'''

# ui_capture.py
import subprocess
import sys
from PIL import Image
import numpy as np
import os
import argparse

def run_random_ui_app(app, width, height, widget_list, widget_count, output_bin, delay_count):
    subprocess.run([app, '-w', str(width), '-h', str(height), '-c', str(widget_count), '-t', ','.join(widget_list), '-o', output_bin, '-d', str(delay_count)])

def convert_binary_to_image(binary_file, width, height, output_file):
    # Read binary data
    with open(binary_file, 'rb') as file:
        data = file.read()

    # Convert to a NumPy array and reshape
    img_array = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 4))

    # Create an image from the array
    image = Image.fromarray(img_array, 'RGBA')

    # Save the image
    image.save(output_file)

def capture_ui(app, width, height, output_folder, iterations, widget_list, widget_count, delay_count):
    for i in range(iterations):
        output_bin = os.path.join(output_folder, f"dump_{i}.bin")
        image_output = os.path.join(output_folder, f"ui_{i}.png")
        
        run_random_ui_app(app, width, height, widget_list, widget_count, output_bin, delay_count)
        convert_binary_to_image(output_bin, width, height, image_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture UI and convert to image.')
    parser.add_argument('--app_path', required=True, help='Path to the random UI application')
    parser.add_argument('--iterations', required=True, type=int, default=10, help='Number of UIs to generate')
    parser.add_argument('--width', type=int, required=True, default=800, help='Width of the UI')
    parser.add_argument('--height', type=int, required=True, default=600, help='Height of the UI')
    parser.add_argument('--widget_count', required=True, type=int, help='Number of widgets to create in each iteration')
    parser.add_argument('--widget_list', required=True, nargs='+', help='List of widgets for the UI')
    parser.add_argument('--output_folder', required=True, help='Folder to save the output images')
    parser.add_argument('--delay_count', type=int, default=10, help='Amount of times the timer handler shall be called with a fixed delay before capturing the UI')

    args = parser.parse_args()

    capture_ui(
        os.path.abspath(args.app_path),
        args.width,
        args.height,
        os.path.abspath(args.output_folder),
        args.iterations,
        args.widget_list,
        args.widget_count,
        args.delay_count
    )