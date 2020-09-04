import odlpet.siemens.listmode.petlink.format32 as petlink32

import numpy as np
import os

def is_uint32(n):
    return isinstance(n, np.uint32)

def get_packets_from_data_file(filename, dtype=np.uint32):
    """
    input: 
    filename: data filename with path, will be checked for correct file extension
    dtype:    default is np.uint32, and only implemented for this alternativ now
           in the future also 64-bit data may be handled
    output:   
    listmode_packets: array of listmode packets (i.e. includes all data, with events, delays, time markers, etc)
    """
    
    if not dtype == np.uint32:    
        raise TypeError("listmode.get_packets is only implemented for uint32 data")
                
    with open(filename, 'rb') as file:
        listmode_packets = np.fromfile(file, dtype = dtype)
        
    return listmode_packets
#----------------------------------------------------    
def get_events_from_packets(listmode_packets, verbose=False):
    """
    input: 
    listmode_packets: array of listmode packets 
    verbose: information printed to screen if True
    output:   
    listmode_eventss: array of listmode events
    """
    
    # get events    
    is_event = petlink32.EVENT.compare(listmode_packets)
    listmode_events = listmode_packets[is_event]
            
    if verbose:
        print("listmode_events =", listmode_events, " length = ", len(listmode_events))
                
    return listmode_events
#----------------------------------------------------    
def get_bin_addresses_from_packets(listmode_packets, verbose=False):
    """
    input: 
    listmode_packets: array of listmode packets 
    verbose: information printed to screen if True
    output:   
    bin_addresses: array of bin addresses corresponding to listmode events
    """
    
    # get the events
    listmode_events = get_events_from_packets(listmode_packets, False)

    # get the corresponding bin adresses
    bin_addresses = petlink32.BIN_ADDRESS.evaluate(listmode_events)
        
    if verbose:
        print("bin addresses =", bin_addresses, " length = ", len(bin_addresses))
    
    return bin_addresses    
#----------------------------------------------------    
def get_bin_address_from_packet(listmode_packet):
    """
    input: 
    listmode_packet: a listmode packet
    output:   
    bin_address: bin address corresponding to listmode_packet
    """
    
    # get the corresponding bin adresses
    return petlink32.BIN_ADDRESS.evaluate(listmode_packet)

    
#----------------------------------------------------    
def is_event_prompt(listmode_event):
    """
    input: 
    listmode_event: a listmode event
    output:   
    is_packet_prompt: True if event is a prompt event
    """
    
    if not is_event(listmode_event):
        raise TypeError("listmode.is_event_prompt called with non-event packet")
    
    # get the corresponding bin adresses
    return petlink32.PROMPT.compare(listmode_event)

def is_event(listmode_event):
    """
    input: 
    listmode_event: a listmode event
    output:   
    is_event: True if packet is an event 
    """
    # todo: move checks like this to petlink
    if is_uint32:
        # get the corresponding bin adresses
        return petlink32.EVENT.compare(listmode_event)
    else:
        raise NotImplementedError #64 bit version not implemented
    
#----------------------------------------------------    
def get_timeslices_from_packets(listmode_packets, time_low=None, time_high=None, verbose=False):
    """
    input: 
    listmode_packets:   array of listmode packets 
    time_low:           lower limit for time marker selection
    time_high:          upper limit for time marker selection
    verbose:            information printed to screen if True
    output:   
    time_at_markers:    array of time markers [ms]
    listmode_timeslices: an array of listmode packets for each time marker
    """
    
    # get the time markers
    is_elapsed_time_markers = petlink32.ELAPSED_TIME_MARKER.compare(listmode_packets) # interpret content 
    time_markers = listmode_packets[is_elapsed_time_markers]
        
    elapsed_time_per_packet = np.cumsum(is_elapsed_time_markers) # how many ms have passed, per packet
    
    # get the elapsed time at each marker
    time_at_markers = petlink32.TIME_MS.evaluate(time_markers)
    
    # slice the listmode packets at the time markers
    split_indices = np.nonzero(is_elapsed_time_markers)[0] 
    listmode_timeslices = np.split(listmode_packets, split_indices)
        
    return time_at_markers, listmode_timeslices

#----------------------------------------------------    
def create_events_time_array_from_packets(listmode_packets, verbose=False):
    """
    input: 
    listmode_packets:   array of listmode packets
    verbose:            information printed to screen if True
    output:   
    events_time:         array of elapsed time for each event in listmode_packets[ms]
    """
    
    # get the time markers for all packets
    is_elapsed_time_markers = petlink32.ELAPSED_TIME_MARKER.compare(listmode_packets) # interpret content 
    
    # create time array for all packets
    packets_time = np.cumsum(is_elapsed_time_markers) # how many ms have passed, per packet
    
    # find events
    is_events = petlink32.EVENT.compare(listmode_packets)
    events_time = packets_time[is_events]
    
    if verbose:
        print("events time =", events_time, " length = ", len(events_time))
        
    return events_time

#----------------------------------------------------        
def create_time_to_ba_dictionary(listmode_packets, time_low=None, time_high=None, verbose=False):
    """
    input: 
    listmode_packets:   array of listmode packets 
    time_low:           lower limit for time marker selection
    time_high:          upper limit for time marker selection
    verbose:            information printed to screen if True
    output:   
    time_dict: dictionary of time markers [ms], with an array of bin addresses for each time marker
    """
    
    # get time markers and time slices
    time_at_markers, listmode_timeslices = get_timeslices_from_packets(listmode_packets)
    
    # create the time dictionary
    time_dict = {}

    # find start time
    if time_low and time_low in time_at_markers:
        start = np.where(time_at_markers==time_low)[0][0]
    else:    
        start = 0
    
    # find end time
    if time_high and time_high in time_at_markers:
        stop = np.where(time_at_markers==time_high)[0][0]
    else:    
        stop = len(time_at_markers) - 1      
    
    # define time range
    time_range = range(start,stop,1)
    
    # fill the dictionary
    for i in time_range:
        time_ms = time_at_markers[i]
        time_dict[time_ms] = get_bin_addresses_from_packets(listmode_timeslices[i])
        
    if verbose:
        print("Time dictionary created, length = ", len(time_dict))
        
    return time_dict    

#----------------------------------------------------    
def get_timestamp_from_ba_in_dict(time_dict, ba):
    """
    input: 
    time_dict:  dictionary of time markers [ms], with an array of bin addresses for each time marker
    ba:         the bin address to find the time marker for
    output:   
    ba_time:    the time marker [ms] for the bin address, if not found in time_dict ba_time = -1
    """
    
    for i in range(0,len(time_dict)):
        res = np.where(time_dict[i] == ba)
        if len(res)>0 and len(res[0])>0:
            return i
            
    return -1    