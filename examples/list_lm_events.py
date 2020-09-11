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

def list_lm_events(hdr_path, num_rows=1000, comp_from_hdr=True, time_low=None, time_high=None, verbose=True, stir_output_file=None):
    """
    input: 
    hdr_path: the header file with path
    num_rows: limits the number of printed rows, if None all rows are printed
    verbose: will not show info on screen, default is True, output will be printed
    output_file: if given the output will also be printed to a .txt-file
    output:
    will print out information about all events in the listmode file, up to a limit num_rows
    """

    # import listmode packets based on header file
    listmode_datastruct = dataimport.import_data_from_hdr(hdr_path, verbose=verbose)
    
    listmode_params = listmode_datastruct.params
    # print general info
    print_general_information(listmode_params, verbose)    

    listmode_packets = listmode_datastruct.packets 
    # get the events from the packets
    events = listmode.get_events_from_packets(listmode_packets, verbose)
    # create events_time array, i.e. array with elapsed time for each event
    events_time = listmode.create_events_time_array_from_packets(listmode_packets, verbose)
    
    # get the compression object, used e.g. to calculate crystal pairs
    # the mashing is not handled correctly this way, seems to assume span=1
    print("Creating the compression using odlpet 'Compression'")
    compression = Compression.from_stir_scanner_name(listmode_params.scanner_system) 
    # therefore, to get the correct span etc, update compression object from header data
    if comp_from_hdr: # this is default 
        print("Updating the compression object using 'header_extractor.compression_from_hdr'")
        compression = header_extractor.compression_from_hdr(str(listmode_params.hdr_path), compression_obj = compression, verbose = False)
         
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
            
    _time = -1        
    for k in range(0, range_end):
        if events_time is not None:
            _time = events_time[k]
        print_listmode_event_full_description(k, events[k], listmode_params, _time, compression)
        
    return listmode_datastruct, compression
    
#----------------------------------------------------      
def print_general_information(params, verbose = True):
    if verbose:
        print(" ")
        if params.is_listmode:
            print("General listmode data information:")
        else:
            print("General sinogram data information:")
        
        print("hdr path = ", params.hdr_path)
        print("scanner = ", params.scanner_system)
        print("TOF bins = ", params.num_TOF_bins)
        print("TOF mashing = ", params.TOF_mash_factor)
        print("span = ", params.span)
        print("number of rings = ", params.num_rings)
        print("segment table = ", params.segment_table)
        print("histogram shape = ", params.histogram_shape)
        print("histogram labels = ", params.histogram_labels)
        print(50*"-")
        

#----------------------------------------------------        
def print_listmode_event_full_description(idx, event, _params, time_marker=-1, _compression=None):
    
    if not _params.is_listmode:
        raise Exception("print_listmode_event_full_description is meant for listmode data")
     
    # unravel to get the corresponding histogram
    ba = listmode.get_bin_address_from_packet(event)
    TOF_LOR = np.unravel_index(ba, _params.histogram_shape)
    
    tof_bin = []
    if _params.num_TOF_bins > 1: tof_bin = TOF_LOR[0]
    sino_num = TOF_LOR[len(TOF_LOR)-3]
    angle_num = TOF_LOR[len(TOF_LOR)-2]
    radial_num = TOF_LOR[len(TOF_LOR)-1]

    if listmode.is_event_prompt(event):
        prompt_or_delay = "p"
    else:
        prompt_or_delay = "d"

    print(50*"=")        
    print("event index:", idx)
    if (time_marker >= 0): print("time_marker:",time_marker)
    print("bin_address: ", listmode.get_bin_address_from_packet(event))
    print("np.unravel bin address:", TOF_LOR)
    print("TOF bin: {}".format(tof_bin))
    print("sinogram num: {}".format(sino_num))

    if not _compression:
        print(50*"=")      
    else:
        actual_angle, radial_offset, crystal_pair_avg = detector_pair.get_crystal_pair_avg(angle_num, radial_num, _compression)  
        actual_angles, radial_offset2, crystal_pair_all = detector_pair.get_crystal_pair_all(angle_num, radial_num, _compression)  
        ring_sum, ring_diff, ring_pair = detector_pair.get_ring_pair(_params.segment_table, sino_num, _params.span)
        print("angle num: {} => uncompressed to {}".format(angle_num, actual_angle))
        print("radial num: {} => radial position {}".format(radial_num, radial_offset))
        print("crystal_pair (average):", crystal_pair_avg)
        print("crystal_pairs (all):", crystal_pair_all)
    
        print("rings:",ring_pair)
    
        #Coincidence p (c:15,r:33,l:0)-(c:283,r:22,l:0)
        for cp in crystal_pair_all:
            print("Coincidence {} (c:{}, r:{}, l:0)-(c:{}, r:{}, l:0) ".format(prompt_or_delay, cp[0],ring_pair[0],cp[1],ring_pair[1]))
        
        if tof_bin: # if time of flight, make sure all delayeds are in the tof bin
            if listmode.is_event_prompt(event):
                assert tof_bin < _params.num_TOF_bins, " tof bin = {}, prompt must be in one of the tof bins".format(tof_bin)
            else:
                assert tof_bin == _params.num_TOF_bins, " tof bin = {}, delayeds must be in bin nr num_TOF_bins+1, i.e. with index num_TOF_bins".format(tof_bin)
            
        print(50*"=")        
    
