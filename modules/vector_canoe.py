from py_canoe import CANoe, wait
from time import sleep
import win32com.client, time
from .util.process_util import count_running_processes, kill_process

def some_cfg_loaded(canoe_exe: str) -> str | None:
  '''Check if a configuration file is loaded in CANoe.
  Args:
      canoe_exe: The name of the CANoe executable.
  Returns:
      str | None: 
        - Returns the full path of the configuration file if loaded, otherwise None.'''

  # Check if the application is running  
  #if count_running_processes(canoe_exe) != 1:
  #  return None
  try:
    app = win32com.client.Dispatch("CANoe.Application")
    name = app.Configuration.Name
    full = app.Configuration.FullName
    return full if name else None
  
  except Exception as e:
    return None
   
  

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
  
  try:
    app = win32com.client.Dispatch("CANoe.Application")
  except Exception as e:
    return None
  
  return cfg_full_name if app.Measurement.Running else None


def is_measurement_running(canoe_exe: str) -> bool:
  '''Check if measurement is running
  Args:
    canoe_exe: The name of the CANoe executable.
    
  Returns:
    bool: True if the measurement is running, False otherwise.'''
    
  try:
    app = win32com.client.Dispatch("CANoe.Application")
    return app.Measurement.Running
  
  except Exception as e:
    return False
  

    
def start_measurement(cfg_path: str, canoe_exe: str, wit_ui: bool = False) -> int:
  '''Start the CANoe application with the specified configuration file.
  Args:
    cfg_file: The path to the CANoe configuration file.
    canoe_exe: The name of the CANoe executable.
  Returns:
    bool: True if the application started successfully, False otherwise.'''
  
  # Process running
  CFG_LOADED_AND_MEASUREMENT = 0
  CFG_LOADED_AND_NOT_MEASUREMENT = 1
  CFG_NOT_LOADED = 2
  TOO_MANY_OPEN_CAONE_INSTANCES = 3
  CANOE_CLOSED = 4
  
  canoe_exe_count = count_running_processes(canoe_exe)
  loaded_path  = some_cfg_loaded(canoe_exe)
  meas_is_running = is_measurement_running(canoe_exe)
  check = type(cfg_path) is str and type(loaded_path) is str and cfg_path == loaded_path
  
  # Check status 
  if check  and meas_is_running:
    status = CFG_LOADED_AND_MEASUREMENT
    return 1 # Measurement is running yet
  
  elif check and not meas_is_running:
    status = CFG_LOADED_AND_NOT_MEASUREMENT
  
  elif canoe_exe_count == 1:
    status = CFG_NOT_LOADED
  
  elif canoe_exe_count > 1:
    status = TOO_MANY_OPEN_CAONE_INSTANCES
    if kill_process(canoe_exe):
      status = CANOE_CLOSED
    else:
      return 8000 # Kill process error
  
  else:
    status = CANOE_CLOSED
  
  
  # Open CANoe application with the specified configuration file
  try:
    canoe_inst = CANoe()
  except Exception as e:
    return 8000 # Cannot define instance
  
  try:
    canoe_inst.open(canoe_cfg=cfg_path, visible=wit_ui, prompt_user=False, auto_stop=True)
  except Exception as e:
    kill_process(canoe_exe)
    
  
  try:
    canoe_inst.start_measurement()
  except Exception as e:
    return 8002 # Cannot start measurement

  return 0 # Done

