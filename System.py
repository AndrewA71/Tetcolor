import sys
from pathlib import Path, PurePath


def resource_path(relative_path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent

    return PurePath(bundle_dir, relative_path)
