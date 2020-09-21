   

class FileDefinitions():
    # store file extensions for listmode header and data file
    LISTMODE_HDR_EXT  = ".hdr"
    LISTMODE_DATA_EXT = ".l"
    LISTMODE_STIR_HDR_EXT = ".l.hdr"

    # store file extensions for sinogram header and data file
    SINOGRAM_HDR_EXT  = ".s.hdr"
    SINOGRAM_DATA_EXT = ".s"

class ScannerModels():    
    # define scanner model tags
    SCANNER_MCT = "MCT"
    SCANNER_MMR = "MMR"
    SCANNER_1104 = 1104
    SCANNER_2008 = 2008
    
class DataTypes():
    # listmode keys
    LISTMODE = "listmode"
    LM_PACKET = "listmode packet"
    LM_BIN_ADDRESS = "listmode bin address"
    LM_EVENT = "listmode event"
    LM_PROMPT = "listmode prompt"
    
    # sinogram keys
    SINOGRAM = "sinogram"

    def is_listmode(data_type):
        if data_type == LISTMODE:
            return True
        else:
            return False
            
    def is_sinogram(data_type):
        if data_type == SINOGRAM:
            return True
        else:
            return False            
 
