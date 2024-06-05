import os, sys


def resource_path(relative_path):
    """The function creates alternative versions of the file 
    paths for optional portability via PyInstaller.

    Args:
        None
    """

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)