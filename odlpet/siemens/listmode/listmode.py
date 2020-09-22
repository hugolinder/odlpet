import odlpet.siemens.listmode.petlink.format32 as petlink32

import numpy as np
import os

class DataStruct():
    def __init__(self, params, verbose=False):
        
        if not params or params == None:
            raise Exception("listmode init DataStruct requires input params")
        
        if not params.filename:
            raise Exception("listmode.DataStruct(): filename is missing in listmode params, cannot create DataStruct")
        
        self.params = params
        
        self.packets = get_packets_from_data_file(params.filename, verbose) 
        
       
def is_uint32(n):
    return isinstance(n, np.uint32)

def get_packets_from_data_file(filename, verbose=False, dtype=np.uint32):
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
    if verbose:
        print("listmode_packets =", listmode_packets, " length = ", len(listmode_packets))
       
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
def get_prompts_from_events(listmode_events, events_time=[], verbose=False):
    """
    input: 
    listmode_events: array of listmode events
    verbose: information printed to screen if True
    output:   
    listmode_prompts: array of listmode prompts
    """
    
    # get prompts    
    is_prompt = petlink32.PROMPT.compare(listmode_events)
    listmode_prompts = listmode_events[is_prompt]
    
    if verbose:
        print("listmode_prompts =", listmode_prompts, " length = ", len(listmode_prompts))
        
    if events_time == []:
        return listmode_prompts  
    else:  
        events_prompts_time = events_time[is_prompt]
        
    if verbose:
        print("prompts_time =", events_prompts_time, " length = ", len(events_prompts_time))
        
    return listmode_prompts, events_prompts_time

#----------------------------------------------------        
def get_delayeds_from_packets(listmode_packets, verbose=False):
    """
    input: 
    listmode_packets: array of listmode packets 
    verbose: information printed to screen if True
    output:   
    listmode_delayeds: array of listmode delayed events (in the last TOF bin)
    """
    
    # get delayed    
    listmode_events = get_events_from_packets(listmode_packets, False)
    is_delayed = petlink32.DELAY.compare(listmode_events)
    listmode_delayeds = listmode_events[is_delayed]
            
    if verbose:
        print("listmode_delayeds =", listmode_delayeds, " length = ", len(listmode_delayeds))
                
    return listmode_delayeds    
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
    
    # returr if prompt or not
    return petlink32.PROMPT.compare(listmode_event)
#----------------------------------------------------    
def is_event_delayed(listmode_event):
    """
    input: 
    listmode_event: a listmode event
    output:   
    is_packet_delayed: True if event is a delayed event
    """
    
    if not is_event(listmode_event):
        raise TypeError("listmode.is_event_delayed called with non-event packet")
    
    # returr if delayed or not
    return petlink32.DELAY.compare(listmode_event)
#----------------------------------------------------    
def is_event(listmode_event):
    """
    input: 
    listmode_event: a listmode event
    output:   
    is_event: True if packet is an event 
    """
    # todo: move checks like this to petlink
    if is_uint32(listmode_event):
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
def create_events_time_arrays_from_packets(listmode_packets, time_range=None, verbose=False):
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
    events_all = listmode_packets[is_events]
    # get the corresponding time array 
    events_time_all = packets_time[is_events]
    
    if time_range != None:
        # select the events in time_range
        try:
            _indices = np.array([], dtype=np.uint32)
            for _t in time_range:
                _indices = np.append(_indices, np.where(events_time_all==_t))

            events = events_all[_indices]
            events_time = events_time_all[_indices]

        except:
            raise Exception("listmode: Failed to filter events with time_range = {} ".format(time_range)) 
    else:
        _indices = np.arange(len(events_time_all))
        events_time = events_time_all
        events = events_all
        
    if verbose:
        if time_range != None:
            print("time range for event selection =", time_range, " => ", list(time_range))
        else:
            print("time_range = None, i.e. no limitation on selected events")
        print("indices =", _indices, " length =", len(_indices))
        print("events =", events, " length =", len(events))
        print("events time =", events_time, " length =", len(events_time))
                
    return events, events_time, _indices
#----------------------------------------------------    
def create_unraveled_histogram_from_packets(listmode_packets, histogram_shape, order='C', dtype=np.uint32, verbose=False):
    bin_addresses = get_bin_addresses_from_packets(listmode_packets, verbose=False);
    histogram_1D = np.zeros(np.prod(histogram_shape), dtype=dtype)
    np.add.at(histogram_1D, bin_addresses, 1)
    histogram_unraveled = np.reshape(histogram_1D, histogram_shape, order=order)
    if verbose:
        print("created {}D histogram with shape = {} ".format(len(histogram_shape), histogram_shape))
    return histogram_unraveled