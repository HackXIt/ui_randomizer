import os
from typing import List
from typing import Generator
import logging

def replace_in_file(replace: tuple, file: str):
    """
    Replace occurence of replace[0] with replace[1] in a file

    Assumes correct tuple length of 2 and that file exists
    """
    logging.debug("Replacing %s with %s in %s", replace[0], replace[1], file)
    with open(file, 'r+') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = line.replace(replace[0], replace[1])
            lines[i] = line
        f.seek(0)
        f.writelines(lines)
        f.truncate()

def dataset_files(dir: str, skip_directories: List[str], skip_files: List[str]) -> Generator[int, None, None]:
    """
    Generator for dataset files in a directory

    Skips directories and files specified in skip_directories and skip_files

    Returns a generator of absolute file paths
    """
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a directory")
    for root, dirs, files in os.walk(dir):
        logging.debug("%i directories in %s: %s...", len(dirs), root, ' '.join(dirs))
        dirs[:] = [d for d in dirs if d not in skip_directories]
        for file in files:
            if file in skip_files:
                continue
            if file.endswith('.data'):
                logging.debug("Found %s", file)
                yield os.path.join(root, file)

def replace_paths_in_dataset_files(root: str, replace: tuple, skip_directories: List[str] = ['rico', 'test', 'train', 'val'], skip_files: List[str] = ['classes.names']) -> None:
    """
    Recursively replace all paths in a dataset directory

    Skips by default directories named 'rico', 'test', 'train', and 'val' and files named 'classes.names'
    """
    if len(replace) != 2:
        raise ValueError("Argument replace must be a tuple of length 2")
    for file in dataset_files(root, skip_directories, skip_files):
        logging.debug(f"Replacing paths in {file}...")
        replace_in_file(replace, file)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    root_dir = os.path.join(os.getcwd(), 'data')
    replace = (root_dir, "/app/project")
    replace_paths_in_dataset_files(root_dir, replace)