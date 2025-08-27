from modules.vector_canoe import some_cfg_loaded

CANOE_EXE = 'CANoe64.exe'

a = some_cfg_loaded(CANOE_EXE)

if a:
  print(a)
else:
  print('not found')