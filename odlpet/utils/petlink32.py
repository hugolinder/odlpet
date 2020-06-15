class packet_part:
    def __init__(self, lowbit, hightbit, value=None):
        self.lowbit = lowbit
        self.highbit = highbit
        self.value = value
        self.mask = get_mask(lowbit, highbit)

    def evaluate(self, number):
        return (self.mask & number) >> lowbit

    def compare(self, number):
        return evaluate(number) == self.value

def get_mask(lowbit, highbit):
    """ 1s from lowbit (LSB) to highbit (MSB), 0 elsewhere. Example, get_mask(1,2) --> 110 (binary)  """
    size = highbit + 1 - lowbit
    mask = 1
    mask = (mask << size) - 1
    return mask << lowbit

EVENT = packet_part(31, 31, 0)

PROMPT = packet_part(30, 30, 1)

BIN_ADDRESS = packet_part(0, 29)

TIME_TAG = packet_part(30, 31, 0b10)

TIME_MS = packet_part(0, 28) # relative to 1970

MOTION_TAG = packet_part(29, 31, 0b110)

IS_HORIZONTAL_BED = packet_part(31-8, 31, 0b11000100)

HORIZONTAL_BED_POSITION = packet_part(0, 19) # units of 10 mikro-meter

IS_HORIZONTAL_MOVING = packet_part(19+1, 19+1, 1) # "This bit was requested but implementation may be pending." (PetLink)

IS_VERTICAL_BED = packet_part(31-8, 31, 0b11000011) 

VERTICAL_BED_POSITION = packet_part(0, 13) # unknown units

MONITORING_TAG = packet_part(28, 31, 0b1110)

CONTROL_TAG = packet_part(27, 31, 0b1111)