# Import CanOe
from py_canoe import CANoe, wait

cfg_file = r'C:\CanOeService\cfg\MMA_Updated\BODY1_15.cfg'

# Instance of class
print('***********************************************')
print('>>> Create instance')
canoe_inst = CANoe()

STATUS_0_WAIT = 0
STATUS_1_OPEN = 1

while True:
    
    print('***********************************************')
    cmd = input('Write: open, start, info, stop, quit, exit: >')
    status = 0
    match cmd:
        
        case 'open':
            if status == STATUS_0_WAIT:
                canoe_inst.open(canoe_cfg=cfg_file)
                status = STATUS_1_OPEN
        
        case 'start':
            if status == STATUS_1_OPEN:
                canoe_inst.start_measurement()
                
        case 'info':
            if status == STATUS_1_OPEN:
                canoe_version_info = canoe_inst.get_canoe_version_info()
                print(canoe_version_info)
        
        case 'stop':
            if status == STATUS_1_OPEN:
                canoe_inst.stop_measurement()
                status = STATUS_0_WAIT
            
        case 'quit':
            canoe_inst.quit()
        
        case 'exit':
            break

print('***********************************************')
