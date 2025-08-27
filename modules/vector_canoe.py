from py_canoe import CANoe, wait
from time import sleep
import win32com.client, time

from .util.process_util import processes_running, kill_process

def some_cfg_loaded(canoe_exe: str) -> str | None:
  '''Check if a configuration file is loaded in CANoe.
  Args:
      canoe_exe: The name of the CANoe executable.
  Returns:
      str | None: 
        - Returns the full path of the configuration file if loaded, otherwise None.'''

  # Check if the application is running  
  if processes_running(canoe_exe) is None:
    return None
  
  app = win32com.client.Dispatch("CANoe.Application")
  name = app.Configuration.Name
  full = app.Configuration.FullName

  return full if name else None
    

def some_measurement_running(canoe_exe: str) -> str | None:
  '''Check if a measurement is running in CANoe.
  Args:
    canoe_exe: The name of the CANoe executable.
  Returns:
    str | None: 
      - Returns the configuration full path if a measurement is running, otherwise None.'''
  
  cfg_full_name = some_cfg_loaded(canoe_exe)
  
  if cfg_full_name is None:
    return None
  
  app = win32com.client.Dispatch("CANoe.Application")
  
  return cfg_full_name if app.Measurement.Running else None
    
    
def start_app(cfg_path: str, canoe_exe: str, wit_ui: bool = False) -> int:
  '''Start the CANoe application with the specified configuration file.
  Args:
    cfg_file: The path to the CANoe configuration file.
    canoe_exe: The name of the CANoe executable.
  Returns:
    bool: True if the application started successfully, False otherwise.'''
  
  # Process running
  cnt = processes_running(canoe_exe)
  if cnt:
    if len(cnt) > 1:
      kill_process(canoe_exe)
  
  # Open CANoe application with the specified configuration file
  try:
    canoe_inst = CANoe()
    canoe_inst.open(canoe_cfg=cfg_path, visible=wit_ui, prompt_user=False, auto_stop=True)
    canoe_inst.start_measurement()
    return 0

  except Exception as e:
    print(e)
    return 8001

