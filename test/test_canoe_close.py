# Import CanOe
from py_canoe import CANoe, wait
from time import sleep

cfg_file_1 = r'C:\CanOeService\cfg\MMA_Updated\BODY1_15.cfg'
cfg_file_2 = r'C:\CanOeService\cfg\DCM223_Updated\BODY1_15.cfg'

# Instance of class
print('*************************************')
print('>>> Create instance')
canoe_inst = CANoe()


#print('>>> Get CanOe version')
#canoe_version_info = canoe_inst.get_canoe_version_info()
#print(canoe_version_info)

print('')
print('>>> Open')
canoe_inst.open(canoe_cfg=cfg_file_1, visible=True, prompt_user=False, auto_stop=True)

print('')
print('>>> Openned, sleep 10s')
sleep(10.0)

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
print('>>> Informed, sleep 20s')
sleep(20.0)

if False:
    print('')
    print('>>> Stop')
    try:
        canoe_inst.stop_measurement()
    except Exception as e:
        print('>> Exception: ', e)


print('>>> Started, sleep 2s')
sleep(2.0)

print('*************************************')

print('>>> Open')
canoe_inst.open(canoe_cfg=cfg_file_2, visible=False, prompt_user=False, auto_stop=True)
print('>>> Openned, sleep 10s')
sleep(10.0)

print('>>> Start')
try:
    canoe_inst.start_measurement()
except Exception as e:
    print('>> Exception: ', e)
    
print('>>> Started, sleep 2s')
sleep(2.0)

print('>>> Get info')
canoe_version_info = canoe_inst.get_canoe_version_info()
print('Running status: ', canoe_inst.get_measurement_running_status)
print('Version info', canoe_version_info)
print('>>> Informed, sleep 20s')
sleep(20.0)


if False:
    print('>>> Stop')

    try:
        canoe_inst.stop_measurement()
    except Exception as e:
        print('>> Exception: ', e)


print('*************************************')
