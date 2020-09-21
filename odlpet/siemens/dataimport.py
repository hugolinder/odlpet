import odlpet.siemens.interfile.header_parser as header_parser
import odlpet.siemens.interfile.header_extractor as header_extractor
from odlpet.siemens.interfile.interfile_keys import InterfileKeys
from odlpet.siemens.key_definitions import DataTypes, FileDefinitions
import os
import odlpet.siemens.listmode.listmode as listmode


class Params():
    def __init__(self):
        
        self.filename = None
        self.hdr_path = None
        
        self.scanner_system = None
        
        self.num_TOF_bins = None
        self.TOF_mash_factor = None
        
        self.span = None
        self.num_rings = None
        self.max_ring_diff = None
        
        self.segment_table = None
        self.histogram_shape = None
        self.histogram_labels = None
        
        self.is_listmode = False
        self.listmode_word_cnt = 0
        
    def get_params_from_header(self, hdr_path, verbose=False):
        
        params = Params()
        
        # save header path
        params.hdr_path = hdr_path
        
        # get the header 
        hdr = self.get_header_from_path(hdr_path)
        
        # extract scanner type
        params.scanner_system = header_extractor.extract_scanner_system(hdr)
        if verbose:
            print("scanner system from header file:", params.scanner_system)
        
        # check if listmode data
        params.is_listmode = header_extractor.extract_listmode_info(hdr)[0]
        
        # get data filename
        params.filename = get_data_filename_from_hdr(hdr_path, params.is_listmode)
    
        # segment table 
        params.segment_table = header_extractor.extract_segment_table(hdr)
        
        # span
        params.span = header_extractor.extract_span_num(hdr)
        
        # get Time Of Flight info
        params.num_TOF_bins, params.TOF_mash_factor = header_extractor.extract_TOF_info(hdr)
        
        params.num_rings = header_extractor.extract_num_rings(hdr)
        params.max_ring_diff = header_extractor.extract_max_ring_diff(hdr)
        
        # get listmode word count
        params.wordcnt = header_extractor.extract_listmode_info(hdr)[1]
        
        params.histogram_shape, params.histogram_labels = header_extractor.extract_histogram_shape(hdr)
        
        return params
        
    def get_header_from_path(self, hdr_path):
        if not os.path.isfile(hdr_path):
            raise TypeError("import_data_from_hdr: cannot find file {}".format(hdr_path))
        try:        
            hdr = header_parser.load(hdr_path)
        except:
            raise TypeError("import_data_from_hdr: interfile.header_parser cannot load file {}".format(hdr_path))
        return hdr 
        
def import_data_from_folder(folder_path, data_type=None):
    """
    input: 
    folder_path: the folder with header and data files to import
    output:
    data: the gathered data
    datatype: type of data in file - i.e. "listmode" or "sinogram"
    """
    headers = [p for p in phantom_data.glob("*/"*2 + "*.hdr")] #look two folders down, for header files
    print([p.name for p in headers])
    #continue here...

def import_data_from_hdr(hdr_path, verbose=False):
    """
    input: 
    hdr_path: the header file with path
    data_type: "listmode" or "sinogram", if "None" data_type will be extracted from the header
    output:
    data: the gathered data
    """
    
    params = Params()
    data_params = params.get_params_from_header(hdr_path)
    
    if data_params.is_listmode:
        data_struct = listmode.DataStruct(data_params, verbose)
    else: 
        raise NotImplementedError("import_sinogram_data has not been implemented yet")
    
    return data_struct
    
def get_data_filename_from_hdr(hdr_path, is_listmode):
    """
    input: 
    hdr_path: the header filename with path
    is_listmode: True - listmode data is expected, False - sinogram data
    output:
    data_filename: the data filename with path, corresponding to the header file
    data_type: type of data in file - i.e. "listmode" or "sinogram"
    """
    
    if is_listmode:
        data_ext = FileDefinitions.LISTMODE_DATA_EXT # ".l"
    else:
        data_ext = FileDefinitions.SINOGRAM_DATA_EXT # ".s"

    hdr = header_parser.load(hdr_path)
    
    # get header path without file extension
    hdr_path_no_ext = os.path.splitext(hdr_path)[0] 
    
    # get data filename from header, or create from header filename
    data_filename = ""
    if not InterfileKeys.FILENAME in hdr:
        print(">>>>> warning in import_data.get_data_filename_from_hdr: filename is missing in header file, creating from header filename")
        data_filename = hdr_path_no_ext + data_ext
    else:
        data_filename = hdr[InterfileKeys.FILENAME]['value']
        data_filename_no_ext = os.path.splitext(data_filename)[0]
        # check that file
        if (data_filename_no_ext != hdr_path_no_ext[1]):
            print(">>>>> Warning in import_data.get_data_filename_from_hdr:")
            print(">>>>> Mismatch between header filename: '{}'".format(hdr_path))
            print(">>>>> and data filename in header: '{}'".format(data_filename))
            data_filename = hdr_path_no_ext + data_ext    
            print(">>>>> Created new data filename: '{}'".format(data_filename))
            
    if not os.path.isfile(data_filename):
        raise TypeError("import_data.get_data_filename_from_hdr: cannot find data file {} corresponding to hdr file ".format(data_filename, hdr_path))
        
    return data_filename    