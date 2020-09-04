import numpy as np
import odlpet.siemens.detector.offset as offset
import odlpet.siemens.detector.axial as axial

dimension_map = {"TOF":0, "SN":1, "TXA":2, "RO":3}
dimension_map["time of flight"]=0
dimension_map["sinogram number"] = 1
dimension_map["transaxial angle"]=2
dimension_map["radial element"] = 3
    
def get_crystal_pair_avg(angle_num, radial_num, compression, mash_factor=2):
    actual_angle = angle_num * mash_factor
    radial_offset = radial_num - compression.get_num_tangential() //2
    pair = getDetectorPair(actual_angle, radial_offset)
    return actual_angle, radial_offset, pair

def get_crystal_pair_all(angle_num, radial_num, _compression):
    #mash factor is not available in Compression but this should work
    mash_factor = _compression.get_default_num_tangential() // _compression.num_of_views 
    min_actual_angle = angle_num * mash_factor 
    radial_offset = radial_num - _compression.get_num_tangential() //2
    
    # num_crystals (13+1)*48 for mCT, and num_crystals = 2*252 for mMR, according to Scanner.cxx in STIR
    num_crystals = _compression.num_of_views * 2
    
    crystal_pairs = []
    actual_angles = []
    for i in range(mash_factor):
        actual_angle = min_actual_angle + i
        crystal_pairs.append(getDetectorPair(actual_angle, radial_offset, num_crystals))   
        actual_angles.append(actual_angle)
    return actual_angles, radial_offset, crystal_pairs
    
def get_ring_pair(segment_table, sino_num, span_num):
    ring_sum_map, segment_map = axial.get_mi_maps(np.array(segment_table))
    segment_nums = segment_map[sino_num]
    num_segments = len(segment_table)
    segment_directions = offset.get_offset_map(num_segments)
    
    ring_sums = ring_sum_map[sino_num]
    ring_diffs = segment_directions[segment_nums]*span_num
    
    ring_pair = ((ring_sums-ring_diffs)//2, (ring_sums+ring_diffs+1)//2) # choose lower of center, or ((ring_sums-ring_diffs)/2, (ring_sums+ring_diffs+1)/2)
        
    return ring_sums, ring_diffs, ring_pair


    # todo: find better place for this, e.g. in tests
    if len(ring_dict) < index + 1:
        print("warning ",index, " not found, ignoring")
        return True
    
    if not len(ring_dict[index]) == len(expected):
        print("error in sinogram ",index, ", wrong length:", ring_dict[index])
        return False
    
    if not ring_dict[index] == expected:        
        print("error in sinogram ",index, ":", ring_dict[index])
        return False
    return True
    
def getAngleAndElement(d1, d2, ncrystals=14*12*4):
    """
    Calculate the angle and radial element of the LOR between detectors d1, d2
    """
    if d1 > d2:
        d1, d2 = d2, d1
    nangles = ncrystals//2
    angle = ((d1+d2 +nangles+ 1) % (ncrystals))//2
    element = np.abs(d2-d1-nangles)
    if (d1 < angle) or (d2>(angle+nangles)):
        element = -element
    return angle, element

def getDetectorPair(angle, element, ncrystals=14*12*4):
    """ 
    Calculate the crystal/detector pair of a LOR 
    """
    nangles = ncrystals // 2
    d1 = angle
    d2 = angle + nangles
    d1 = d1 + element // 2
    d2 = d2 - (element + 1)//2
    d1 = d1 % ncrystals
    d2 = d2 % ncrystals
    if d1 > d2:
        d1, d2 = d2, d1
    return d1, d2

def test_cycle(ncrystals=4):
    """
    check if getAngleAndElement is the inverse of getDetectorPair
    """
    count = 0
    for d1 in range(ncrystals):
        for d2 in range(ncrystals):
            crystals = np.sort([d1, d2])
            LOR = getAngleAndElement(*crystals, ncrystals)
            cycled_crystals = getCrystalPair(*LOR, ncrystals)
            error = 0
            for c1, c2 in zip(cycled_crystals, crystals):
                if c1 != c2:
                    error += 1
            if error > 0:
                status = [crystals, cycled_crystals, LOR]
                print("ERROR, crystals {} cycled to {} via LOR {}".format(*status))
            count += error
    return count