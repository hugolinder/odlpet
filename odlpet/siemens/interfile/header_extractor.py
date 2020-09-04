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

    
def compression_from_hdr(scanner, hdr_path, compression_obj = None, verbose = False):
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
    
    if verbose: print("determine if listmode or sinogram")
    key = "SMS-MI header name space"
    value = hdr[key]['value']
    is_sinogram = value == "sinogram subheader"
    if verbose:
        dtype = "sinogram" if is_sinogram else "listmode"
        print("assume data is {}, based on {}:={}".format(dtype, key, value))

    # sanity check
    hdr_end = ".s.hdr"
    is_sinogram2 = hdr_path.endswith(hdr_end) 
    if verbose: print("check 'header path {} ends with {}' = {}".format(hdr_path, hdr_end, is_sinogram2))
    if is_sinogram != is_sinogram2:
        print("error, unexpected header content and file extension (e.g. '.s.hdr') mismatch, will exit")
        exit()
            
    if compression_obj is None: 
        if verbose: print("create scanner default compression")
        compression_obj = Compression(scanner)
        
    if verbose: print("create list of target odlpet compression attributes to update")
    attribute_names = ["span_num", "max_num_segments", "num_of_views", "num_non_arccor_bins", "data_arc_corrected"]
    hdr_names = ["axial compression", "maximum ring difference", "number of views", "number of projections", "applied corrections"]
    
    if verbose: print("compression attributes {} \n, corresponds to {}\n, in header".format(attribute_names, hdr_names))
    hdr_matrix_names = ["sinogram views", "sinogram projections"]
    n_easy = 2 
    n_matrix = 2
    if not is_sinogram: 
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
    if is_sinogram:
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
    
def extract_histogram(hdr):
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

    if (TOF_bins > 0):
        sizes.append(TOF_bins + 1) #+1 is for randoms (delayed)
        labels.append("time of flight bins")
                
    if (listmode):
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