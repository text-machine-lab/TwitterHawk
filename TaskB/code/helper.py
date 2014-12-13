"""Utility methods."""
import os
import os.path
import errno


def map_files(files):
    """Maps a list of files to basename -> path."""
    output = {}
    for f in files: #pylint: disable=invalid-name
        basename = os.path.splitext(os.path.basename(f))[0]
        output[basename] = f
    return output