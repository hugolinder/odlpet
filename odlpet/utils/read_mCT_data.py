import interfile
from odlpet.scanner.compression import Compression

def extract_family(hdr, name):
    """
    header is assumed to be the output of interfile.load(header_path), that is a parsed header file
    name is the start of a "matrix key", 
        e.g. "scale factor" corresponding to "scale factor ... [x]" 
        or "matrix size" corresponding to "matrix size [x]"
        where x is an integer
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
    hdr = interfile.load(hdr_path)
    if verbose: print("determine if listmode or sinogram")
    key = "SMS-MI header name space"
    value = hdr[key]['value']
    is_sinogram = value == "sinogram subheader"
    if verbose:
        dtype = "sinogram" if is_sinogram else "listmode"
        print("assume data is {}, based on {}:={}".format(dtype, key, value))

    if verbose:
        hdr_end = ".s.hdr"
        is_sinogram2 = hdr_path.endswith(hdr_end) # sanity check
        if verbose: print("check 'header path {} ends with {}' = {}".format(hdr_path, hdr_end, is_sinogram2))
        if is_sinogram != is_sinogram2:
            print("warning, unexpected header content and file extension (e.g. '.s.hdr') mismatch")
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
    hdr_line = hdr.get(hdr_name)
    if verbose: 
        hdr_name2 = "'is {} one of the {}'".format(hdr_value, hdr_name)
        print("interpret attribute {} as {}".format(name, hdr_name2))
    value = False # Siemens apparent default: unless stated, not corrected for
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