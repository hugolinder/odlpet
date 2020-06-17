class packet_part:
    def __init__(self, lowbit, highbit, value=None, name="packet part"):
        self.lowbit = lowbit
        self.highbit = highbit
        self.value = value
        self.mask = get_mask(lowbit, highbit)
        self.name = name

    def evaluate(self, number):
        return (self.mask & number) >> self.lowbit

    def compare(self, number):
        return self.evaluate(number) == self.value

    def __repr__(self):
        names = [self.name]
        names.append("low bit = {}".format(self.lowbit))
        names.append("high bit = {}".format(self.highbit))
        if self.value is not None:
            names.append("value = {0:b} (base 2)".format(self.value))
        names.append("mask = {0:b}".format(self.mask))
        return "\n".join(names)

def get_mask(lowbit, highbit):
    """ 1s from lowbit (LSB) to highbit (MSB), 0 elsewhere. Example, get_mask(1,2) --> 110 (binary)  """
    size = highbit + 1 - lowbit
    mask = 1
    mask = (mask << size) - 1
    return mask << lowbit

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
#   skip 3.2.4 page 12

