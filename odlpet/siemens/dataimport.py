import odlpet.siemens.interfile.header_parser as header_parser
import odlpet.siemens.interfile.header_extractor as header_extractor
from odlpet.siemens.interfile.interfile_keys import InterfileKeys
from odlpet.siemens.key_definitions import DataTypes, FileDefinitions
import os
import odlpet.siemens.listmode.listmode as listmode

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

def import_data_from_hdr(hdr_path, data_type=None):
    """
    input: 
    hdr_path: the header file with path
    data_type: "listmode" or "sinogram", if "None" data_type will be extracted from the header
    output:
    data: the gathered data
    datatype: type of data in file - i.e. "listmode" or "sinogram"
    """

    if not os.path.isfile(hdr_path):
        raise TypeError("import_data_from_hdr: cannot find file {}".format(hdr_path))
    try:        
        hdr = header_parser.load(hdr_path)
    except:
        raise TypeError("import_data_from_hdr: interfile.header_parser cannot load file {}".format(hdr_path))
    
    if not data_type:
        is_listmode = header_extractor.extract_listmode_info(hdr)[0]
        if is_listmode:
            data_type = DataTypes.LISTMODE
        else:
            data_type = DataTypes.SINOGRAM
    
    if data_type == DataTypes.LISTMODE:
        data = import_listmode_data(hdr_path)
    elif data_type == DataTypes.SINOGRAM:
        data = import_sinogram_data(hdr_path)
    else:
        raise TypeError("import_data_from_hdr: unknown data type, possible data types are '{}' and '{}'".format(DataTypes.LISTMODE, DataTypes.SINOGRAM))
    
    return data
    
def import_listmode_data(hdr_path):
    """
    input: 
    hdr_path: the header file with path
    output:
    data: the gathered data
    datatype: type of data in file - i.e. "listmode" or "sinogram"
    """
    filename = get_data_filename_from_hdr(hdr_path, True)
    data = listmode.get_packets_from_data_file(filename) #returns [0] data array and [1] LM_PACKET
    wrdcnt = header_extractor.extract_listmode_info(header_parser.load(hdr_path))[1]
    
    return data

def import_sinogram_data(hdr_path):
    raise NotImplementedError("import_sinogram_data has not been implemented yet")
    
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
        raise TypeError("import_data.get_data_filename_from_hdr: cannot find file {}".format(data_filename))
        
    return data_filename    