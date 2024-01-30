# UI Randomizer
The UI randomizer is a python script that leverages the binary of the UI generator, and uses it to generate multiple random UI in sequence. 

It is helpful in making the generator much more user-friendly, since it can be used to generate a large number of UIs with a single command, without having to repeatedly run the generator manually.

Since the label data from the generator still needs to be normalized, the randomizer will pre-process the annotation files and place the data in the correct folder structure for training the model.

### Usage
`python ui_capture.py [arguments]`

#### Arguments

The script accepts several arguments to customize the dataset generation:

    -p or --app_path: (Required) Path to the random UI generator binary.
    -i or --iterations: Number of user interface screenshots to generate (default: 10).
    -t or --widget_types: (Required) List of widget types to be included in the UI. The names of these types must match the naming convention of the generator (e.g. button, checkbox, etc.).
    --width: Width of the UI screenshot (default: 250).
    --height: Height of the UI screenshot (default: 250).
    -o or --output_folder: (Required) Folder path to save the output images.
    -d or --delay_count: Delay count for UI capture (default: 10).
    --split_widgets: Option to split widgets into subfolders.
    -l or --layout: The used layout in the generation:
        - `none` (randomized absolute positions)
        - `grid` (randomized cell placement - grid size is the amount widgets squared, e.g. 9x9 for 9 widgets)
        - `flex` (randomized flexbox placement)
    -r or --split_ratio: Split ratio for train, validation, and test datasets.
    -s or --single: Create only a single widget per iteration.
    -m or --multi: Number of widgets to create per iteration (if multiple).

#### Example
An example command might look like this:

`python ui_capture.py -p path/to/ui/generator -i 20 -t button checkbox -o path/to/output -d 5 --split_widgets`

The script will generate the UI images and organize them into a dataset placed into the specified output folder. It creates necessary subfolders for images and labels. The script will also automatically pre-process the label data _(i.e. normalize pixel values and replace widget names with class IDs)_.

### Known issues

- The code is not very well written and currently just performs the bare minimum to get the job done. It is not very error-friendly and could use some refactoring.
