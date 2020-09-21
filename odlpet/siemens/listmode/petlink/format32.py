# parts and logic for 32 bit packets 

class document_section:
    def __init__(self, name, packets, pages = None):
        self.packets = packets
        self.name = name
        self.pages = pages

    def __repr__(self):
        names = [self.name]
        packet_names = "\n".join([packet.name for packet in self.packets])
        context = "section({} )"
        attributes= "name = {}\n, packets = \n{}".format(self.name, packet_names)
        if self.pages is not None:
            attributes = attributes + "\n, pages = {}".format(self.pages)
                                
        return context.format(attributes)



#   PETLink documentation, start at page 4
#   3.1 Overview, page 4
EVENT = packet_part(31, 31, 0)
TIME_TAG = packet_part(31-1, 31, 0b10)
MOTION_TAG = packet_part(31-2, 31, 0b110)
GANTRY_MOTION_POSITION_TAG = MOTION_TAG
MONITORING_TAG = packet_part(31-3, 31, 0b1110)
CONTROL_TAG = packet_part(31-3, 31, 0b1111)
#   3.2 event packet
PROMPT = packet_part(30, 30, 1)
BIN_ADDRESS = packet_part(0, 29)
#   skip SPECT event packet (obsolete)
#   skip 4 maintenance packets, page 5
#   3.2.1 time and dead time, page 6
ELAPSED_TIME_MARKER = packet_part(31-2, 31, 0b100)
TIME_MS = packet_part(0, 28) #seems to start at 0
DEAD_TIME_MARKER = packet_part(31-2, 31, 0b101)
DEAD_TIME_BLOCK = packet_part(19, 19+9)
DEAD_TIME_SINGLES_RATE = packet_part(0, 18) #units vary
#   skip expanded format, page 7
#   3.2.2 Gantry motion and position, page 8
#   skip 3 legacy packets 
#       detector rotation (SPECT)
#       head I "A" radial position
#       head II "B" radial position
IS_HORIZONTAL_BED = packet_part(31-7, 31, 0b11000100)
HORIZONTAL_BED_POSITION = packet_part(0, 19) # units of 10 mikro-meter
IS_HORIZONTAL_MOVING = packet_part(19+1, 19+1, 1)
IS_VERTICAL_BED = packet_part(31-7, 31, 0b11000011) 
VERTICAL_BED_POSITION = packet_part(0, 13) # unknown units
#   skip gantry Left/Right position
#   skip source axial position and rotation, page 9
#   skip HRRT single photon source position
#   skip 3.2.3
BASIC_GATING = packet_part(31-4, 31, 0b11100)
BASIG_GATING_EXPANSION_FORMAT_CONTROL = packet_part(31-7,31-5)
BASIC_GATING_E0_G = packet_part(0, 7)
BASIC_GATING_E0_D = packet_part(0, 5) 
# Physiological Data (e.g. Respiratory Phase) Field: 0-5. 
# D content only has validity if flag bit P=1
BASIC_GATING_E0_P = packet_part(6) 
# Physiological (e.g. Respiratory) Flag Bit – High Tru
BASIC_GATING_E0_C = packet_part(7) 
# Cardiac “R Wave” Flag Bit – High True. This bit is intended to be the primary trigger control 
# for driving the automatic FPGA-driven Gating Buffer switching in designs such as the Smart DRAM.

#   skip 3.2.4 page 12

