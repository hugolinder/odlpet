#The general packet classes from the current petlink32.py
#This provides some structure to the content of the PETLinkt guideline. 

class PacketFormat:
    """Implementation of Packet format details from PETLINK guideline. 
    For simplicity, packet formats have a partition of its bits into parts, corresponding to the fields in the guideline. 
    Thus, the more complicated 64-bit format would be represented as several different PacketFormats, 
    instead of one complicated format. 
    A packet is simply a number."""
    def __init__(self, description=None, name=None, partition=None, visual_guide=None, parts = None, comment=None, numbits=32):
        self.description = description
        #if self.description is not None: # To Do: parse description for automatic creation based on petlink text
        self.name = name
        self.partition = partition
        self.visual_guide = visual_guide
        self.parts = parts
        self.comment = comment
        self.numbits = numbits
        
    def compare(self, packet):
        """ compares with all value fields, returns True when all value fields compare True. """
        result = True
        for part in self.parts:
            if part.value is not None:
                result *= part.compare(packet)
        return result

    def evaluate(self, packet):
        """ return sequence of packet number evalations, one per field in the packet. """
        return [part.evaluate(packet) for part in self.parts]
    
    def details(self):
        return "{}({})".format(self.__class__.__name__, "**{}".format(str(self.__dict__)))
    
    def __repr__(self):
        return "{}(name={})".format(self.__class__.__name__, self.name)

class PacketPart:
    """A simpler version of the packet fields in the guideline. 
    A part is a range into the packet bits, with some properties for evaluation.
    A packet is simply a number.
    """

    def __init__(self, lowbit, highbit=None, value=None, name=None, description=None, is_twos_complement = False):
        self.name = name
        self.lowbit = lowbit
        if highbit is None:
            highbit = lowbit + 1
        self.highbit = highbit
        self.nbits = highbit - lowbit
        self.value = value
        self.mask = ((1 << self.nbits) - 1) << lowbit
        self.mask_hexadecimal = "{0:x}".format(self.mask)
        #self.mask_nibbles = nibble_string(self.mask, self.nbits)
        self.is_twos_complement = is_twos_complement
    
    def evaluate(self, packet):
        """Evaluate packet, in mask, relative to lowbit. Perform sign extension if a twos complement value """
        value = (self.mask & packet) >> self.lowbit
        if self.is_twos_complement:
            signbit = (value >> (self.nbits-1)) & 1
            value = signbit*(value - (1 << nbits)) + (signbit == 0)*value
        return value
    
    def compare(self, packet):
        return self.evaluate(packet) == self.value
    
    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, "**{}".format(str(self.__dict__)))