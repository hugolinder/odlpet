# parts, packets and logic for 32 bit packets 

from odlpet.siemens.listmode.petlink.packet import PacketFormat, PacketPart
#
#   PETLink documentation, start at page 4
#   3.1 Overview, page 4
EVENT = PacketPart(31, 32, 0)
TIME_TAG = PacketPart(31-1, 32, 0b10)
MOTION_TAG = PacketPart(31-2, 32, 0b110)
GANTRY_MOTION_POSITION_TAG = MOTION_TAG
MONITORING_TAG = PacketPart(31-3, 32, 0b1110)
CONTROL_TAG = PacketPart(31-3, 32, 0b1111)
#   3.2 event packet
PROMPT = PacketPart(30, 31, 1)
DELAY = PacketPart(30, 31, 0)
BIN_ADDRESS = PacketPart(0, 30)
PROMPT_PACKET = PacketFormat(name = 'PET Bin-Address Event Packet (prompt)', parts = [EVENT, PROMPT, BIN_ADDRESS])
DELAY_PACKET = PacketFormat(name = 'PET Bin-Address Event Packet (delay)', parts = [EVENT, DELAY, BIN_ADDRESS])
#   skip SPECT event packet (obsolete)
#   skip 4 maintenance packets, page 5
#   3.2.1 time and dead time, page 6
ELAPSED_TIME_MARKER = PacketPart(31-2, 32, 0b100)
TIME_MS = PacketPart(0, 29) #seems to start at 0
DEAD_TIME_MARKER = PacketPart(31-2, 32, 0b101)
DEAD_TIME_BLOCK = PacketPart(19, 19+10)
DEAD_TIME_SINGLES_RATE = PacketPart(0, 19) #units vary
#   skip expanded format, page 7
#   3.2.2 Gantry motion and position, page 8
#   skip 3 legacy packets 
#       detector rotation (SPECT)
#       head I "A" radial position
#       head II "B" radial position
IS_HORIZONTAL_BED = PacketPart(31-7, 32, 0b11000100)
HORIZONTAL_BED_POSITION = PacketPart(0, 29) # units of 10 mikro-meter
IS_HORIZONTAL_MOVING = PacketPart(19+1, 19+2, 1)
IS_VERTICAL_BED = PacketPart(31-7, 32, 0b11000011) 
VERTICAL_BED_POSITION = PacketPart(0, 14) # unknown units
#   skip gantry Left/Right position
#   skip source axial position and rotation, page 9
#   skip HRRT single photon source position
#   skip 3.2.3
BASIC_GATING = PacketPart(31-4, 32, 0b11100)
BASIG_GATING_EXPANSION_FORMAT_CONTROL = PacketPart(31-7,31-4)
BASIC_GATING_E0_G = PacketPart(0, 8)
BASIC_GATING_E0_D = PacketPart(0, 6) 
# Physiological Data (e.g. Respiratory Phase) Field: 0-5. 
# D content only has validity if flag bit P=1
BASIC_GATING_E0_P = PacketPart(6) 
# Physiological (e.g. Respiratory) Flag Bit – High Tru
BASIC_GATING_E0_C = PacketPart(7) 
# Cardiac “R Wave” Flag Bit – High True. This bit is intended to be the primary trigger control 
# for driving the automatic FPGA-driven Gating Buffer switching in designs such as the Smart DRAM.

#   skip 3.2.4 page 12

