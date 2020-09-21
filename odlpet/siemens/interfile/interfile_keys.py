
class InterfileKeys():

    #Interfile keys
    SCANNER_SYSTEM = "originating system"
    
    # data filename
    FILENAME = "name of data file"
    
    # segment table, gives number of sinograms per segment
    SEG_TABLE = "segment table"
    NUM_SEGMENTS = "number of segments"
    
    # Time of flight 
    TOF_NUM_BINS = "number of TOF time bins"
    TOF_MASH     = "TOF mashing factor"
    
    # Listmode header
    LM_WORD_CNT  = "total listmode word counts"
    LM_NUM_PROJ = "number of projections"
    LM_NUM_VIEWS = "number of views"    
    
    # Sinogram header
    HISTO_NUM_SINO  = "total number of sinograms"
    HISTO_NUM_PROJ  = "sinogram projections"
    HISTO_NUM_VIEWS = "sinogram views"

    SPAN_NUM      = "axial compression"
    NUM_RINGS     = "number of rings"
    MAX_RING_DIFF = "maximum ring difference"
