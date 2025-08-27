# Import CanOe
from py_canoe import CANoe, wait
from time import sleep

from kill_app import close_app, list_app



cfg_file_1 = r'C:\CanOeService\cfg\MMA_Updated\BODY1_15.cfg'
cfg_file_2 = r'C:\CanOeService\cfg\DCM223_Updated\BODY1_15.cfg'

canoe_exe = 'CANoe64.exe'
canoe_inst = CANoe()

def start_app(cfg_file: str, canoe_exe: str = 'CANoe64.exe'):
    
    # Close process
    close_app(canoe_exe)
    canoe_inst.open(canoe_cfg=cfg_file_1, visible=False, prompt_user=False, auto_stop=True)
    try:
        canoe_inst.start_measurement()
        return True
    except Exception as e:
        return False
    




# Instance of class
print('*************************************')
print('>>> Get process')
list_app(find=canoe_exe)
sleep(1.0)

print('\n>>> Kill process')
close_app('CANoe64.exe')
sleep(5.0)

print('\n*************************************')
print('\n>>> Create instance')
canoe_inst = CANoe()

print('\n*************************************')
print('>>> Open', cfg_file_1)
canoe_inst.open(canoe_cfg=cfg_file_1, visible=False, prompt_user=False, auto_stop=True)

print('')
print('>>> Openned, sleep 10s')
sleep(10.0)

print('')
print('>>> Get process')
list_app(find=canoe_exe)
sleep(1.0)

print('')
print('>>> Start')
try:
    canoe_inst.start_measurement()
except Exception as e:
    print('>> Exception: ', e)
    
print('')
print('>>> Started, sleep 2s')
sleep(2.0)

print('')
print('>>> Get info')

canoe_version_info = canoe_inst.get_canoe_version_info()
print('Running status: ', canoe_inst.get_measurement_running_status)
print('Version info', canoe_version_info)
print('')
print('>>> Informed, sleep 2s')
sleep(2.0)

print('')
print('>>> Stop')
try:
    canoe_inst.stop_measurement()
except Exception as e:
    print('>> Exception: ', e)


print('')
print('>>> End')
print('*************************************')

sleep(15.0)

#exit()

print('')
print('*************************************')
print('*************************************')
print('*************************************')

print('*************************************')
print('>>> Get process')
list_app(find=canoe_exe)
sleep(1.0)

print('\n>>> Kill process')
close_app('CANoe64.exe')
sleep(5.0)

print('\n*************************************')
print('>>> Open', cfg_file_2)
canoe_inst.open(canoe_cfg=cfg_file_2, visible=False, prompt_user=False, auto_stop=True)

print('')
print('>>> Openned, sleep 10s')
sleep(10.0)

print('')
print('>>> Get process')
list_app(find=canoe_exe)
sleep(1.0)

print('')
print('>>> Start')

attempt = 0

while attempt < 3:
    try:
        canoe_inst.start_measurement()
        break
    except Exception as e:
        print('>> Attempt', attempt)
        print('>> Exception: ', e)
        print()
    finally:
        attempt = attempt + 1
        sleep(5.0)
        
    
print('')
print('>>> Started, sleep 2s')
sleep(2.0)

print('')
print('>>> Get info')

canoe_version_info = canoe_inst.get_canoe_version_info()
print('Running status: ', canoe_inst.get_measurement_running_status)
print('Version info', canoe_version_info)
print('')
print('>>> Informed, sleep 2s')
sleep(2.0)

print('')
print('>>> Stop')
try:
    canoe_inst.stop_measurement()
except Exception as e:
    print('>> Exception: ', e)


print('')
print('>>> End')
print('*************************************')
