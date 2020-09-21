import numpy as np
from pathlib import Path
import os.path
import shutil

def gate(ranges, header_path, output_dir):
    """extract selected listmode data into a new interfile.
    
    copies the source header and data indicated by the header path from the ranges into output directory.
    """
    # these parameters should preferably be read from the header file
    dtype = np.int32
    if Path(header_path).name.endswith('.l.hdr'):
        body_path = Path(header_path).with_suffix("") #remove .hdr
    else:
        body_path = Path(header_path).with_suffix(".l") 
    # possibly optimize so that the entire file is not read
    # get offset, count from ranges, and update ranges
    # not necessarily good when there are many ranges
    with open(body_path, 'rb') as fid:
        packets = np.fromfile(fid, dtype=dtype)
    selection = np.concatenate([packets[r] for r in ranges])
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    dst = Path(output_dir) / Path(header_path).name
    shutil.copyfile(header_path, dst)
    dst = dst.with_name(body_path.name)
    with open(dst, 'wb') as fid:
        selection.tofile(fid)       
    return 0

