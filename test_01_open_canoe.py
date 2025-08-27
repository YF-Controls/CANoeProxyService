# Import CanOe
from py_canoe import CANoe, wait
from time import sleep
import win32com.client, time

from modules.vector_canoe import some_measurement_running, start_app, some_cfg_loaded

cfg_file_1 = r'C:\CanOeProxy\cfg\MMA_Updated\BODY1_15.cfg'
cfg_file_2 = r'C:\CanOeProxy\cfg\DCM223_Updated\BODY1_15.cfg'
CANOE_EXE = 'CANoe64.exe'

if __name__ == '__main__':
    print('#################################################')
    print('Exe: ')
    
    cfg_name = some_cfg_loaded(CANOE_EXE)
    if cfg_name:
        print('Cargado ', cfg_name)
    else:
        print('Nada cargado')
    
    cfg_name = some_measurement_running(CANOE_EXE)
    if cfg_name:
        print('Corriendo ', cfg_name)
    else:
        print('No está corriendo nada')
    
    
    exit(0)
    
    done = start_app(cfg_file_1, CANOE_EXE, True)
    if done == 0:
        print('Executando')
    else:
        print('Algo fue mal ', done)
    
    print('#################################################')
