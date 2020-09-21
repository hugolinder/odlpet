import numpy as np


def get_mi(rm, seg, seg_sizes):
    min_rm = (seg_sizes[0] - seg_sizes[seg])//2
    rm_offset = rm - min_rm
    min_mis = np.cumsum(seg_sizes) - seg_sizes
    return min_mis[seg] + rm_offset


def untangle_mi(mi, seg_sizes):
    """ input: mi, segment table
    return rm, seg """
    max_mi = np.cumsum(seg_sizes) - 1 # per segment
    seg = np.searchsorted(max_mi, mi)
    min_mi = max_mi + 1 - seg_sizes
    rm_offset = mi - min_mi[seg]
    min_rm = (seg_sizes[0] - seg_sizes[seg])//2
    rm = rm_offset + min_rm
    return rm, seg

def get_mi_maps(seg_tab):
    """mi_maps: from 1 dimensional michelogram index mi to 2 underlying dimensions
    return mi_rs, mi_seg    (=mi_ringmean_map, mi_segment_map) """
        
    num_sino = np.sum(seg_tab)
    mi_seg = np.empty(num_sino, dtype=int)
    mi_rm = np.empty_like(mi_seg)

    min_rm = (seg_tab[0] - seg_tab ) //2
    mi_b= 0
    for seg_num, seg_size in enumerate(seg_tab):
        mi_a = mi_b
        mi_b += seg_size
        mi_seg[mi_a:mi_b] = seg_num
        mi_rm[mi_a:mi_b] = np.arange(seg_size) + min_rm[seg_num] 
            
    return mi_rm, mi_seg