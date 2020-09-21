import numpy as np
def fix_bin_address(lm_in, lm_out, shape=(14, 621, 168, 400), fix_dim=0, fix_value=0, verbose=False):
    """
    set the bin address coordinates to a fixed value
    parameters listmode in, out are paths
    By default sets TOF to 0
    """
    with open(lm_in, 'rb') as fid:  
        packets = np.fromfile(fid, dtype=np.int32)
    is_event = ((packets >> 31) & 1) == 0 
    events = packets[is_event]
    ba = events & 0X3FFFFFFF
    remains = events-ba
    ba = np.array(np.unravel_index(ba, shape))
    if verbose:
        print("bin coordinates \n{}".format(ba))
    def f(x):
        """convert fix parameters"""
        if x is None:
            y = []
        elif np.array(x).ndim == 0:
            y = np.array(x)[None] # numpy trick for expanding dims
        return y
    fix_dim = f(fix_dim)
    fix_value = f(fix_value)
    if verbose:
        print("fix dim {} to value {}".format(fix_dim, fix_value))
    for dim, val in zip(fix_dim, fix_value):
        ba[fix_dim] = val
    ba = np.ravel_multi_index(tuple(ba), shape)
    events = remains + ba
    packets[is_event] = events
    with open(lm_out, 'wb') as fid: 
        fid.write(packets)
    if verbose:
        print('done')

    # very much a copy of above. generalize?
def trim_bin_address(lm_in, lm_out, shape, fix_dim=None, fix_value=None):
    """
    set the bin address coordinates to a fixed value
    """
    with open(lm_in, 'rb') as fid:
        packets = np.fromfile(fid, dtype=np.int32)
    is_event = ((packets >> 31) & 1) == 0
    events = packets[is_event]
    ba = events & 0X3FFFFFFF
    remains = events-ba
    ba = np.array(np.unravel_index(ba, shape))
    print(unravel_ba)
    def f(x):
        if x is None:
            y = []
        elif np.array(x).ndim == 0:
            y = np.array(x)[None] # numpy trick for expanding dims
        return y
    fix_dim = f(fix_dim)
    fix_value = f(fix_value)
    keep = []
    for dim, val in zip(fix_dim, fix_value):
        keep.append(ba[fix_dim] == val)
    packet_keep = np.ones_like(is_event) 
    packet_keep[is_event] = np.any(keep, axis=0)
    packets = packets[keep]
    with open(lm_out, 'wb') as fid: 
        fid.write(packets)
    print('done')