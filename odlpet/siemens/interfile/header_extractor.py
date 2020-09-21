import odlpet.siemens.interfile.header_parser as header_parser
from odlpet.scanner.compression import Compression
from odlpet.siemens.key_definitions import ScannerModels
from odlpet.siemens.interfile.interfile_keys import InterfileKeys as keys
import os
import numpy as np

# to do: make more general, all names for one thing. separate key file?
# then update extract_histogram


def extract_family(hdr, name):
    """
    header is assumed to be the output of header_parser.load(header_path), that is a parsed header file
    name is the start of a "matrix key", 
        e.g. "scale factor" corresponding to "scale factor ... [x]" 
        or "matrix size" corresponding to "matrix size [x]"
        where x is an integer
    family is part of the name
    """
    matched_keys = []
    for key in hdr.keys():
        if key.count(name) > 0:
            matched_keys.append(key)
    def order(key):
        return key[-2] # extract x from "name ... [x]"
    matched_keys.sort(key=order)
    return [hdr[key]['value'] for key in matched_keys]

    
def compression_from_hdr(hdr_path, scanner=None, compression_obj = None, verbose = False):
    """
    input: 
    scanner: an odlpet scanner object
    hdr_path: the path to a interfile header
    compression =None: a odlpet compression to update
    verbose = False: if verbose: print step commit descriptions
    """
    if verbose: print("verbose description of steps enabled with verbose = {}".format(verbose))
    if verbose: print("parse header file at path")
    hdr = header_parser.load(hdr_path)
    
    # check if listmode 
    is_listmode = extract_listmode_info(hdr)[0]

    if compression_obj is None:
        if scanner is None:
            raise Exception("header_extractor: cannot create compression object without either scanner or compression object")
        if verbose: print("creating scanner default compression object")
        compression_obj = Compression(scanner)
    
    span_num = extract_span_num(hdr)
    num_segments = np.ceil(extract_num_segments(hdr) / 2)
    max_diff_ring = extract_max_diff_ring
    
    attribute_names = ["span_num", "max_num_segments", "max_diff_ring", "num_of_views", "num_non_arccor_bins", "data_arc_corrected"]
    hdr_names = ["axial compression", "number of segments", "maximum ring difference", "number of views", "number of projections", "applied corrections"]
    
    if verbose: print("compression attributes {} \n, corresponds to {}\n, in header".format(attribute_names, hdr_names))
    hdr_matrix_names = ["sinogram views", "sinogram projections"]
    n_easy = 2 
    n_matrix = 2
    if is_listmode: 
        n_easy = n_easy + n_matrix
        n_matrix = 0
    easy_attributes = attribute_names[:n_easy]
    matrix_attributes = attribute_names[n_easy:(n_easy+n_matrix)]
    
    if verbose: 
        pairs = [(name, getattr(compression_obj, name)) for name in attribute_names]
        print("show target initial attributes (name, value) \n = {}".format(pairs))
    
    if verbose: print("search for corresponding compression parameters in hdr and update")
    
    # direct mappings
    def update_attr(name, value):
        if value is None:
            print("Error, no info on {} in header. Parameter not updated. ".format(name))
        else:
            setattr(compression_obj, name, value)		

    for name, hdr_name in zip(easy_attributes, hdr_names[:n_easy]):
        if verbose: print("interpret attribute {} as {}".format(name, hdr_name))
        field = hdr.get(hdr_name)
        value = None if field is None else field['value']
        update_attr(name, value)
    
    # matrices 
    if not is_listmode:
        if verbose: print("extract lists for matrix")
        hdr_families = ["matrix axis label", "matrix size"]
        matrix_info = [extract_family(hdr, family) for family in hdr_families]
        if verbose: 
            for pair in zip(hdr_families, matrix_info):
                print(pair)

        def extract_matrix_value(hdr_name):
            value = None
            if matrix_info[0].count(hdr_name) > 0:
                dim_index = matrix_info[0].index(hdr_name)
                fields = ["{}[{}]".format(family, dim_index+1) for family in hdr_families]
                if verbose: print("'{}:={}' indicates {}".format(fields[0], hdr_name, fields[1]))
                value = matrix_info[1][dim_index]
            else:
                 if verbose: print("warning, no matching matrix axis label found in header")
            return value

        for name, hdr_name in zip(matrix_attributes, hdr_matrix_names):
            if verbose: 
                hdr_name2 = hdr_families[1] + " [{}]".format(hdr_name)
                print("interpret attribute {} as {}".format(name, hdr_name2))
            value = extract_matrix_value(hdr_name)
            if value is None and (hdr_name == hdr_matrix_names[0]):
                hdr_name = "plane"
                if verbose: print("try backup header field name '{}' for '{}'".format(hdr_name, name))
                value = extract_matrix_value(hdr_name)
                confirmation = value is not None 
                if verbose: print("confirm: backup ok = {}".format(confirmation))
            update_attr(name, value)
    
    # compare      
    attr_index = -1
    name, hdr_name = attribute_names[attr_index], hdr_names[attr_index]
    hdr_value = "radial arc-correction"
    if verbose: 
        hdr_name2 = "'is {} one of the {}'".format(hdr_value, hdr_name)
        print("interpret attribute {} as {}".format(name, hdr_name2))
    
    value = False # Siemens apparent default: unless stated, not corrected for
    hdr_line = hdr.get(hdr_name)
    if hdr_line is None:
        if verbose: print("no corrections")
    else:
        corrections = hdr_line['value'] # a sequence of applied corrections
        if verbose: print("{}:= {}".format(hdr_name, corrections))
        value = corrections.count(hdr_value) > 0
        update_attr(name, value)	
        
    if verbose: 
        pairs = [(name, getattr(compression_obj, name)) for name in attribute_names]
        print("show target updated attributes (name, value) \n = {}".format(pairs))
    if verbose: print("return")
    
    return compression_obj

def extract_max_diff_ring(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    max_diff_ring: the maximum ring difference
    """
    
    max_diff_ring = 0
    
    if keys.MAX_RING_DIFF in hdr:
        max_diff_ring = hdr[keys.MAX_RING_DIFF]['value']
    
    return max_diff_ring
    
def extract_max_ring_diff(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    max_ring_diff: the maximum ring difference
    """
    
    max_ring_diff = 0
    
    if keys.MAX_RING_DIFF in hdr:
        max_ring_diff = hdr[keys.MAX_RING_DIFF]['value']
    
    return max_ring_diff

def extract_span_num(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    span_num: the span number
    """
    
    span_num = 0
    
    if keys.SPAN_NUM in hdr:
        span_num = hdr[keys.SPAN_NUM]['value']
    
    return span_num

def extract_num_rings(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    num_rings: the number of rings in scanner
    """
    
    num_rings = 0
    
    if keys.NUM_RINGS in hdr:
        num_rings = hdr[keys.NUM_RINGS]['value']
    
    return num_rings
    
    
def extract_num_non_arccor_bins(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    num_non_arccor_bins: the maximum ring difference
    """
    
    #STIR: 'applied corrections' keyword not found. Assuming non-arc-corrected data
    
    num_non_arccor_bins = 0
    
    if keys.MAX_RING_DIFF in hdr:
        num_non_arccor_bins = hdr[keys.MAX_RING_DIFF]['value']
    
    return num_non_arccor_bins

    
    
def extract_arc_correction(hdr):
    
    name = "data_arc_corrected"
    hdr_name = "applied corrections"
    hdr_value = "radial arc-correction"
        
    if verbose: 
        hdr_name2 = "'is {} one of the {}'".format(hdr_value, hdr_name)
        print("interpret attribute {} as {}".format(name, hdr_name2))
    
    value = False # Siemens apparent default: unless stated, not corrected for
    hdr_line = hdr.get(hdr_name)
    if hdr_line is None:
        if verbose: print("no corrections")
    else:
        corrections = hdr_line['value'] # a sequence of applied corrections
        if verbose: print("{}:= {}".format(hdr_name, corrections))
        value = corrections.count(hdr_value) > 0
        update_attr(name, value)	 
    return data_arc_corrected
    
def extract_num_segments(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    num_segments: number of segments
    """
    
    num_segments = 0
    
    if keys.NUM_SEGMENTS in hdr:
        num_segments = hdr[keys.NUM_SEGMENTS]['value']
    
    return num_segments
    
def extract_TOF_info(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    tof_bins: number of Time Of Flight bins (default = 0)
    tof_mashing_factor: Time Of Flight mashing factor (default = 1)
    """
    
    TOF_bins = 0
    TOF_mash_factor = 1
    
    if keys.TOF_NUM_BINS in hdr:
        TOF_bins = hdr[keys.TOF_NUM_BINS]['value']
    if keys.TOF_MASH in hdr:
        TOF_mash_factor = hdr[keys.TOF_MASH]['value']
    
    return TOF_bins, TOF_mash_factor    
    
def extract_segment_table(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    segment_table: list with number of sinograms per segment
    """
    
    if keys.SEG_TABLE in hdr:
        segment_table = hdr[keys.SEG_TABLE]['value']
    else:
        segment_table = []
    
    return segment_table  
    
def extract_histogram_shape(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    histogram_shape: array with histogram dimensions for Siemens data
    
        the order for Siemens data is 
                [TOF, number of sinograms, number of transaxial bins, number of axial bins] if the data has TOF, and 
                [number of sinograms, number of transaxial bins, number of axial bins] if the data does not have TOF
        
    """
     # extract matrix size 
     # to do: make general, for mMR also
    
    sizes = []
    labels = []
    
    TOF_bins, TOF_mash_factor = extract_TOF_info(hdr)
    listmode = extract_listmode_info(hdr)

    # for mCT listmode the order is tof_bin, num_sinograms, num_views, num_projections
    # not sure if mCT sinogram has the same order?
    # for mMR data the number of tof bins = 1 but time of flight is not included => assuming not TOF bin should be used
                
    if (listmode):
        if (TOF_bins > 1):
            sizes.append(TOF_bins + 1) #+1 is for randoms (delayed)
            labels.append("time of flight bins")
        if keys.SEG_TABLE in hdr:
            # in listmode the number of sinograms is not given but can be calculated as the sum of sinograms per each segment
            nr_of_sinograms = np.sum(hdr[keys.SEG_TABLE]['value'])
            sizes.append(nr_of_sinograms)
            labels.append("number of sinograms")
        if keys.LM_NUM_VIEWS in hdr:
            sizes.append(hdr[keys.LM_NUM_VIEWS]['value'])
            labels.append("sinogram views")
        if keys.LM_NUM_PROJ in hdr:
            sizes.append(hdr[keys.LM_NUM_PROJ]['value'])
            labels.append("sinogram projections")
    else:
        if (TOF_bins > 1):
            sizes.append(TOF_bins + 1) #+1 is for randoms (delayed)
            labels.append("time of flight bins")
        if keys.HISTO_NUM_SINO in hdr:
            sizes.append(keys.HISTO_NUM_SINO)
            labels.append("number of sinograms")
        if keys.HISTO_NUM_VIEWS in hdr:
            sizes.append(hdr[keys.HISTO_NUM_VIEWS]['value'])
            labels.append("sinogram views")
        if keys.HISTO_NUM_PROJ in hdr:
            sizes.append(hdr[keys.HISTO_NUM_PROJ]['value'])
            labels.append("sinogram projections")
            
    return sizes, labels
    
def extract_listmode_info(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    is_listmode: True if listmode data
    listmode_wordcnt: number of listmode words
    """
    
    is_listmode = False
    listmode_wordcnt = 0
    
    if keys.LM_WORD_CNT in hdr:
        is_listmode = True
        listmode_wordcnt = hdr[keys.LM_WORD_CNT]['value']
        
    return is_listmode, listmode_wordcnt  


def extract_scanner_system(hdr):
    """
    input: 
    hdr: the header dictionary extracted from the interfile header file
    output:
    scanner_name: mCT for Siemens system 1104, or mMR for Siemens system 2008
    """
    
    if keys.SCANNER_SYSTEM in hdr:
        scanner_system = hdr[keys.SCANNER_SYSTEM]['value']
    else:
        raise TypeError("extract_header_info: cannot extract scanner system from header file, aborting.")
    
    if scanner_system == ScannerModels.SCANNER_1104:
        return ScannerModels.SCANNER_MCT
    elif scanner_system == ScannerModels.SCANNER_2008:
        return ScannerModels.SCANNER_MMR
    else:
        raise TypeError("extract_header_info: unknown scanner system {}, expected {} or {}".format(scanner_system, ScannerModels.SCANNER_1104, ScannerModels.SCANNER_2008))