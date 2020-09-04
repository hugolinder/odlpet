
class DataTypes():
    LISTMODE = "listmode"
    
    LM_PACKET = "listmode packet"
    LM_BIN_ADDRESS = "listmode bin address"
    LM_EVENT = "listmode event"
    LM_PROMPT = "listmode prompt"

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
            
    