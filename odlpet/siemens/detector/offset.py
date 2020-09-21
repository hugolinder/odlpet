import numpy as np

# this next part is for the 'offset' data structures [0, +1, -1, +2, -2, ...] of segments and TOF
def get_offset(num):
    mod2 = (num % 2)
    offset = (num + mod2) // 2 #0,1,1,2,2, ...
    sign = 2*mod2-1 #-,+,-,+,...
    return sign*offset

def get_offset_bin(offset):
    mod2 = 1*(offset > 0)
    offset = np.abs(offset)
    return offset*2 - mod2

def get_offset_map(size):
    """ offset map: return [-0,+1,-1, +2, -2,...] of length size. """
    offsets = np.arange(size)
    offsets[0: :2] *= -1
    offsets = np.cumsum(offsets)
    return offsets

def get_offset_map_inverse(size):
    """ 
    inverse of offset map: negative indices get mapped to where they belong
    let x = (size-1)//2 (size is odd)
    map from [0,1,....,+x,-x,...,-1] to [0,1,3,5,...,2x-1,2x... ,2] 
    the idea is that imap[omap] = np.arange(size), that is the bin numbers
    where omap = get_offset_map(size)
    return imap
    """
    imap = np.zeros(size, dtype=int)
    x = (size-1)//2
    rng = np.arange(x,dtype=int)*2
    imap[1:(x+1)] = rng +1
    imap[-1:-(x+1):-1] = rng + 2
    return imap