from py_canoe import CANoe, wait

# https://pypi.org/project/py_canoe/


canoe_inst = CANoe()

canoe_inst.open(canoe_cfg=r'tests\demo_cfg\demo.cfg')
canoe_inst.start_measurement()
canoe_version_info = canoe_inst.get_canoe_version_info()
print(canoe_version_info)
canoe_inst.stop_measurement()
canoe_inst.quit()

