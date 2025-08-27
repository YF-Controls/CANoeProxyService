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
  

    
def start_measurement(cfg_path: str, canoe_exe: str, wit_ui: bool = False) -> str:
  '''Start the CANoe application with the specified configuration file.
  Args:
    cfg_file: The path to the CANoe configuration file.
    canoe_exe: The name of the CANoe executable.
  Returns:
    str: 0000,{cfg_file} measurement running\n
    8200,Impossible to close {canoe_exe}. Force manually!\n
    8110,Impossible to load CANoe() instance\n
    8111,Impossible to open file: {cfg_file}\n
    8112,Impossible to start measurement, file: {cfg_path}
    '''
  
  # Process running
  STATUS_0_CANOE_CLOSED = 0
  STATUS_1_TOO_MANY_OPEN_CAONE_INSTANCES = 1 
  STATUS_2_CFG_NOT_LOADED = 2
  STATUS_3_CFG_LOADED_DOES_NOT_MATCH_AND_NOT_MEASUREMENT = 3
  STATUS_4_CFG_LOADED_DOES_NOT_MATCH_AND_MEASUREMENT = 4
  STATUS_5_CFG_LOADED_MATCHES_AND_NOT_MEASUREMENT = 5
  STATUS_6_CFG_LOADED_MATCHES_AND_MEASUREMENT = 6
  
  
  count = count_running_processes(canoe_exe)
  
  if count == 0:
    status = STATUS_0_CANOE_CLOSED
  
  elif count > 1:
    status = STATUS_1_TOO_MANY_OPEN_CAONE_INSTANCES
    
    if kill_process(canoe_exe):
      status = STATUS_0_CANOE_CLOSED
    else:
      return f'8200,Impossible to close {canoe_exe}. Force manually!'
  
  else:
    
    loaded_path  = some_cfg_loaded(canoe_exe)
    
    if loaded_path is None:
      status = STATUS_2_CFG_NOT_LOADED
    
    else:
      meas_is_running = is_measurement_running(canoe_exe)
      file_matches = loaded_path == cfg_path
      
      if not file_matches and not meas_is_running:
        status = STATUS_3_CFG_LOADED_DOES_NOT_MATCH_AND_NOT_MEASUREMENT
      
      elif not file_matches and meas_is_running:
        status = STATUS_4_CFG_LOADED_DOES_NOT_MATCH_AND_MEASUREMENT
      
      elif file_matches and not meas_is_running:
        status = STATUS_5_CFG_LOADED_MATCHES_AND_NOT_MEASUREMENT
      
      else:
        status = STATUS_6_CFG_LOADED_MATCHES_AND_MEASUREMENT
        return f'0000,{cfg_path} measurement running'
      
  # Open CANoe application with the specified configuration file
  try:
    canoe_inst = CANoe()
  except Exception as e:
    return f'8110,Impossible to load CANoe() instance'
  
  # Try to open cfg file.
  # We use a while loop because may be when a previous cfg file is in measurement, sometimes it fails.
  # When fails then kill process and try to open again.
  attempt = 0
  done = False
  while True:
  
    try:
      canoe_inst.open(canoe_cfg=cfg_path, visible=wit_ui, prompt_user=False, auto_stop=True)
      done = True
      break # exit loop
      
    except Exception as e:
      if attempt > 0:
        break
      
      kill_process(canoe_exe)
      sleep(1.0)
      attempt += 1
  
  if not done:
    return f'8111,Impossible to open file: {cfg_path}'
  
  # Try to start measurment
  try:
    canoe_inst.start_measurement()
  except Exception as e:
    return f'8112,Impossible to start measurement, file: {cfg_path}'
  
  # Done
  return f'0000,{cfg_path} measurement running'

