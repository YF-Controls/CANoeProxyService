from modules.vector_canoe import *

CANOE_EXE = 'CANoe64.exe'
cfg_file_1 = r'C:\CanOeProxy\cfg\MMA_Updated\BODY1_15.cfg'
cfg_file_2 = r'C:\CanOeProxy\cfg\DCM223_Updated\BODY1_15.cfg'

r = start_measurement('MMA', cfg_file_1, CANOE_EXE, True)

print(r)
