#The general packet classes from the current petlink32.py
#This provides some structure to the content of the PETLinkt guideline. 

class packet:
    def __init__(self, instruction, packet_name = None, part_names = None, is_twos_complement = None):
        instruction_lines = instruction.split("\n")
        if len(instruction_lines) > 1: # alternative input format
            packet_name = instruction_lines[0]
            instruction = instruction_lines[1]
            part_names = instruction_lines[2:]
        self.instruction = instruction
        self.part_names = part_names
        self.is_twos_complement = is_twos_complement
        self.name = packet_name
        instruction = instruction.replace(" ", "") 
        self.len = len(instruction)
        if self.len != 32:
            print("warning, instruction length does not indicate 32 bit packet")
            print("instruction {}, of length {}".format(instruction, self.len))
        self.parts = parse_instruction(instruction) 
        # finally, naming and twos_complement
        if self.part_names is not None: 
            for part, name in zip(self.parts, self.part_names):
                part.name = name
        if self.is_twos_complement is not None:
            for is_signed, part in zip(self.is_twos_complement, self.parts):
                part.is_twos_complement = is_signed

    def __repr__(self):
        parts_info = [part.__repr__() for part in self.parts]
        parts_info = "\n---\n".join(parts_info)
        return "packet(name = {}\ninstruction = {}\nparts = \n{}\n)".format(self.name, self.instruction, parts_info)
        
    def compare(self, number):
        """ compares with all value parts, returns True when all value parts compare True. """
        result = True
        for part in self.parts:
            if part.value is not None:
                result = part.compare(number) == result
        return result

    def evaluate(self, number):
        """ return sequence of number evalations, one per part in the packet. """
        return [part.evaluate(number) for part in self.parts]

class packet_part:
    def __init__(self, lowbit, highbit=None, value=None, name=None, is_twos_complement = False):
        self.lowbit = lowbit
        if highbit is None:
            highbit = lowbit
        self.highbit = highbit
        self.nbits = highbit - lowbit + 1
        self.value = value
        self.mask = get_mask(lowbit, highbit)
        self.name = name
        self.is_twos_complement = is_twos_complement

    def evaluate(self, number, is_twos_complement =None):
        """ evaluate number, in mask, relative to lowbit. Perform sign extension if a twos complement value (default to self) """
        if is_twos_complement is None:
            is_twos_complement = self.is_twos_complement
        value = (self.mask & number) >> self.lowbit
        if is_twos_complement:
            value = sign_extend(value, self.nbits)
        return value

    def compare(self, number):
        return self.evaluate(number) == self.value

    def __repr__(self):
        names = []
        if self.name is not None:
            names.append(self.name)
        names.append( "(lowbit, highbit, nbits) = {}".format( (self.lowbit, self.highbit, self.nbits) ) )
        if self.value is not None:
            names.append("value = {0:b} (base 2)".format(self.value))
        if self.is_twos_complement:
            names.append("field is a twos complement number")
        names.append("mask = {}".format(nibble_string(self.mask)))  
        return "\n".join(names)

def parse_instruction(instruction):
    """ parse doc string, create parts"""
    instruction = instruction.replace(" ", "")
    instruction_parts = [] # first, split instruction into parts
    part_string = ""
    part_char = instruction[0]
    for char in instruction:
        if not (char == part_char): # that is, not AA, 00, 11, ...
            pair = char + part_char
            if not ((pair == "01") or (pair == "10")):
                instruction_parts.append(part_string)
                part_string = ""
                part_char = char
        part_string = part_string + char
    instruction_parts.append(part_string)
    parts = [] # secondly, create a packet part for each instruction part
    offset = 0
    for part in instruction_parts:
        nbits = len(part)
        offset = offset + nbits
        lowbit = len(instruction) - offset
        highbit = lowbit + (nbits-1)
        part_char = part[0]
        is_value = (part_char == '1' ) | (part_char == '0' )
        value = int(part, base=2) if is_value else None
        parts.append(packet_part(lowbit, highbit, value))
    return parts

def get_mask(lowbit, highbit):
    """ 1s from lowbit (LSB) to highbit (MSB), 0 elsewhere. Example, get_mask(1,2) --> 110 (binary)  """
    size = highbit + 1 - lowbit
    mask = 1
    mask = (mask << size) - 1
    return mask << lowbit

def nibble_string(number, nbits=32):
    """ string representation of bits, with nibbles (4 bit chunks) separated by blank spaces """
    number2 = number + (1 << (nbits)) # add a leading 1, so that leading 0's will be included
    res = "{0:b}".format(number2)[1:]  # remove leading 1
    offset = nbits % 4
    pre_nibble = [res[:offset]]
    size_nibbles = (nbits//4)
    nibbles =  [res[(offset+4*n):(offset + 4*(n+1))] for n in range(size_nibbles)]
    res = pre_nibble + nibbles
    return " ".join(res)
 
def sign_extend(number, nbits):
    """ convert a 2's complement natural number to the corresponding integer """
    signbit = (number >> (nbits-1)) & 1
    return signbit*(number - (1 << nbits)) + (signbit == 0)*number