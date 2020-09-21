from odlpet import Scanner

class scanner_data(Scanner):
    name = "Siemens_mCT"
    det_nx_mm = 4
    det_ny_mm = 2*10*0.2027
    num_rings = 4*13+3 # 1  or (4*13  + 3) # in crystals
    #print(ring_size)
    det_radius = 427.6
    average_depth_of_inter = 9.6
    ring_spacing = det_ny_mm
    voxel_size_xy = 4.07283 #one side, mm
    axial_crystals_per_block = num_rings
    trans_crystals_per_block = 13+1
    axial_blocks_per_bucket = 1
    trans_blocks_per_bucket = 4
    ring_size = 12*trans_blocks_per_bucket*trans_crystals_per_block
    num_dets_per_ring = ring_size

    def get_name(self):
        return self.name
    
    def get_num_rings(self):
        return self.num_rings