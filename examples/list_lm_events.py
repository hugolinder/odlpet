from odlpet.scanner.scanner import Scanner
from odlpet.scanner.compression import Compression

from odlpet.siemens.key_definitions import ScannerModels, DataTypes
from odlpet.siemens.interfile.interfile_keys import InterfileKeys as keys

import odlpet.siemens.dataimport as dataimport
import odlpet.siemens.interfile.header_extractor as header_extractor
import odlpet.siemens.interfile.header_parser as header_parser
import odlpet.siemens.listmode.listmode as listmode
import odlpet.siemens.detector.detector_pair as detector_pair

import stir
import numpy as np

# add a limit to the number of lines printed to screen
max_num_lines = 10000

def list_lm_events(hdr_path, num_rows=1000, comp_hdr=True, time_low=None, time_high=None, assert_tof=False, verbose=True, stir_output_file=None):
    """
    input: 
    hdr_path: the header file with path
    num_rows: limits the number of printed rows, if None all rows are printed
    verbose: will not show info on screen, default is True, output will be printed
    output_file: if given the output will also be printed to a .txt-file
    output:
    will print out information about all events in the listmode file, up to a limit num_rows
    """

    # determine which scanner to use
    if verbose:
        print("header path:", hdr_path)
    hdr = header_parser.load(hdr_path)
    scanner_system = header_extractor.extract_scanner_system(header_parser.load(hdr_path))
    if verbose:
        print("scanner system from header file:", scanner_system)
    
    compression = None
    
    # create the scanner
    if scanner_system == ScannerModels.SCANNER_MCT:
        
        # create scanner by using odlpet in combination with STIR 4.0.2
        #scanner = Scanner.from_name('Siemens mCT') 
        
        # alternative 2, by using STIR 4.0.2 directly, but this leads to AttributeError: 'stir.Scanner' object has no attribute 'num_dets_per_ring'
        #scanner = stir.Scanner_get_scanner_from_name(str(ScannerModels.SCANNER_1104)) 
        
        # alternative 3, when using odlpet in combination with STIR 
        stir_scanner = stir.Scanner_get_scanner_from_name('Siemens mCT') 
        scanner = Scanner.from_stir_scanner(stir_scanner) 
        
        # alternative 4, could also create scanner manually by using Siemens_mCT.scanner_data (currently in the scanner catalogue)
        #scanner = Siemens_mCT.scanner_data() 
        
    elif scanner_system == ScannerModels.SCANNER_MMR:
        # alternative 3, when using odlpet in combination with STIR 4.0.0
        stir_scanner = stir.Scanner_get_scanner_from_name('Siemens mMR') 
        scanner = Scanner.from_stir_scanner(stir_scanner) 
    
    if comp_hdr: # this is default 
        print("Creating the compression object using 'header_extractor.compression_from_hdr'")
        compression = header_extractor.compression_from_hdr(scanner, str(hdr_path), compression_obj = None, verbose = False)
    else: # the mashing is not handled correctly this way, seems to assume span=1
        print("Creating the compression using odlpet 'Compression'")
        compression = Compression(scanner)
            
    
    # either way, add a manual fix so that stir can communicate the compression object with STIR
    compression.stir_scanner = stir_scanner #manuell fix
        
    # import listmode packets based on header file
    listmode_packets = dataimport.import_data_from_hdr(hdr_path, DataTypes.LISTMODE)
    
    # load the header information
    hdr = header_parser.load(hdr_path)
    
    # segment table - could also be fetched from compression with compression._get_sinogram_info(), after manipulation
    segment_table = header_extractor.extract_segment_table(hdr)

    # check Time Of Flight
    num_TOF_bins, TOF_mash_factor = header_extractor.extract_TOF_info(hdr)

    # get listmode word count (not used yet though...)
    #listmode_wordcnt = header_extractor.extract_listmode_info(hdr)[1]

    # histogram shape
    histogram_shape, histogram_labels = header_extractor.extract_histogram(hdr)

    # span etc. - from automated_compression
    span = compression.span_num
    
    # print info so far
    print_general_information(num_TOF_bins, TOF_mash_factor, span, scanner.num_rings, segment_table, histogram_shape, histogram_labels, verbose)    
         
    # get listmode events
    events = listmode.get_events_from_packets(listmode_packets, verbose)
    
    # create events_time array, i.e. array with elapsed time for each event
    events_time = listmode.create_events_time_array_from_packets(listmode_packets, verbose)

    if num_rows:
        range_end = num_rows
        print("printing will limited to {} rows".format(num_rows))
    else:
        range_end = len(events)
        if range_end < max_num_lines:
            print("printing is not limited, all {} rows will be printed".format(range_end))
        else:
            print("printing will be limited to {} rows".format(max_num_lines))
            range_end = max_num_lines

    if verbose: 
        projector = compression.get_projector()
        print("projector:", projector)
        
        # this bit does not really belong in list_lm_events, it is just for testing at this stage
        # get bin addresses and accumulate events in histogram
        bin_addresses = listmode.get_bin_addresses_from_packets(listmode_packets, verbose)
        histogram_1D = np.zeros(np.prod(histogram_shape), dtype=np.uint16)
        np.add.at(histogram_1D, bin_addresses, 1)
        order = 'C'
        shape = histogram_shape
        labels = histogram_labels
        volume = np.reshape(histogram_1D, shape, order=order)

    for k in range(0, range_end):
        print_listmode_event_full_description(k, events[k], compression, histogram_shape, segment_table, num_TOF_bins, assert_tof, events_time[k])
    
    
    if stir_output_file is not None:
        projector.proj_data.write_to_file(stir_output_file)
    
    return volume, order, shape, labels, compression, projector, segment_table
    
#----------------------------------------------------      
def print_general_information(num_TOF_bins, TOF_mash_factor, span, nr_of_rings, segment_table, shape, labels, verbose = True):
    if verbose:
        print(" ")
        print("General data information:")
        print("TOF bins = ", num_TOF_bins)
        print("TOF mashing = ",TOF_mash_factor)
        print("span = ", span)
        print("number of rings = ", nr_of_rings)
        print("segment table = ", segment_table)
        print("histogram shape = ", shape)
        print("histogram labels = ", labels)
        print(50*"-")
        

#----------------------------------------------------        
def print_listmode_event_full_description(idx, event, _compression, histogram_shape, segment_table, num_TOF_bins, assert_tof=False, time_marker=-1):
    
    # unravel to get the corresponding histogram
    ba = listmode.get_bin_address_from_packet(event)
    TOF_LOR = np.unravel_index(ba, histogram_shape)
    
    tof_bin = TOF_LOR[0]
    sino_num = TOF_LOR[1]
    angle_num = TOF_LOR[2]
    radial_num = TOF_LOR[3]

    actual_angle, radial_offset, crystal_pair_avg = detector_pair.get_crystal_pair_avg(angle_num, radial_num, _compression)  
    actual_angles, radial_offset2, crystal_pair_all = detector_pair.get_crystal_pair_all(angle_num, radial_num, _compression)  
    ring_sum, ring_diff, ring_pair = detector_pair.get_ring_pair(segment_table, sino_num, _compression.span_num)
        
    if listmode.is_event_prompt(event):
        prompt_or_delay = "p"
    else:
        prompt_or_delay = "d"
        
    print(50*"=")        
    print("event index:", idx)
    if (time_marker >= 0): print("time_marker:",time_marker)
    print("bin_address: ", listmode.get_bin_address_from_packet(event))
    print("np.unravel bin address:", TOF_LOR)
    print("TOF bin {}:".format(tof_bin))
    print("sinogram num {}:".format(sino_num))
    print("angle num {} => uncompressed to {}".format(angle_num, actual_angle))
    print("radial num {} => radial position {}".format(radial_num, radial_offset))
    print("crystal_pair (average):", crystal_pair_avg)
    print("crystal_pairs (all):", crystal_pair_all)
    
    print("rings:",ring_pair)
    
    #Coincidence p (c:15,r:33,l:0)-(c:283,r:22,l:0)
    for cp in crystal_pair_all:
        print("Coincidence {} (c:{}, r:{}, l:0)-(c:{}, r:{}, l:0) ".format(prompt_or_delay, cp[0],ring_pair[0],cp[1],ring_pair[1]))
    
    if assert_tof:
        if listmode.is_event_prompt(event):
            assert tof_bin < num_TOF_bins, " tof bin = {}, prompt must be in one of the tof bins".format(tof_bin)
        else:
            assert tof_bin == num_TOF_bins, " tof bin = {}, delays must be in bin nr num_TOF_bins+1, i.e. with index num_TOF_bins".format(tof_bin)
        
    print(50*"=")        
    
