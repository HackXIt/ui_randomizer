'''
File: random_ui.py
Created on: Thursday, 1970-01-01 @ 01:00:00
Author: HackXIt (<hackxit@gmail.com>)
-----
Last Modified: Monday, 2023-11-20 @ 04:01:02
Modified By:  HackXIt (<hackxit@gmail.com>) @ HACKXIT
-----
'''

# This shit doesn't work very well, since I don't have access to all functionalities like in C
# For example I can't hack my way into the X11 to get a screendump

# random_ui.py (micropython script) - Creates a random UI with the given screen size, number of widgets, and widget types
# Usage: micropython random_ui.py <screen_width>x<screen_height> <num_widgets> <widget_type1,widget_type2,...>
# Example: micropython random_ui.py 240x240 10 btn,label,slider,checkbox,dropdown

# Ignoring import error, as LVGL import only works with the built lv_micropython project
import lvgl as lv
import os
import random
import sys
import time
from lv_utils import event_loop

def create_random_ui(screen_size, num_widgets, widget_types, close_signal_path):
    lv.init()

    # Create an event loop and register SDL display/mouse/keyboard drivers
    loop = event_loop()
    disp_drv = lv.sdl_window_create(screen_size[0], screen_size[1])
    mouse = lv.sdl_mouse_create()
    keyboard = lv.sdl_keyboard_create()

    # Create a screen and randomly add widgets
    scr = lv.obj()
    available_widgets = {
        'btn': lv.btn,
        'label': lv.label,
        'slider': lv.slider,
        'checkbox': lv.checkbox,
        'dropdown': lv.dropdown
    }

    for _ in range(num_widgets):
        widget_type = random.choice([available_widgets[w] for w in widget_types])
        widget = widget_type(scr)
        
        # Adjust alignment method call
        align_type = lv.ALIGN.CENTER
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        widget.align(align_type, x_offset, y_offset)

        if widget_type == lv.label:
            widget.set_text("Random")

    lv.scr_load(scr)
    
    # Access the frame buffer
    fb = lv.sdl_frame_buf_create()
    fb.getter(scr, None)

    # Clean up before closing
    lv.scr_act().del_child(None)  # Delete all children of the active screen
    lv.deinit()  # Deinitialize LVGL

    # Deinitialize SDL components if necessary
    # (This depends on how lv_utils and SDL are set up in your environment)
    # For example:
    # mouse.deinit()
    # keyboard.deinit()
    # disp_drv.deinit()

if __name__ == "__main__":
    # Example usage: micropython random_ui.py 240x240 10 btn,label,slider,checkbox,dropdown
    screen_width, screen_height = map(int, sys.argv[1].split('x'))
    num_widgets = int(sys.argv[2])
    widget_list = sys.argv[3].split(',')
    if(len(sys.argv) > 4):
        close_signal_path = sys.argv[4]
    else:
        close_signal_path = 'close.txt'

    create_random_ui((screen_width, screen_height), num_widgets, widget_list, close_signal_path)