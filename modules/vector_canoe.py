from py_canoe import CANoe, wait
from time import sleep
import win32com.client
import pythoncom
import gc
import os
import logging
from contextlib import contextmanager
from .util.process_util import count_running_processes, kill_process


@contextmanager
def canoe_application_context():
  """Context manager para manejar seguro la aplicación CANoe"""
  pythoncom.CoInitialize()
  app = None
  try:
    app = win32com.client.Dispatch("CANoe.Application")
    yield app
  finally:
    # Limpieza segura
    if app is not None:
      try:
        # No forzamos Quit() para no cerrar CANoe si estaba abierto
        pass
      except:
        pass
      # Eliminar referencia
      del app
    pythoncom.CoUninitialize()

def some_cfg_loaded(canoe_exe: str) -> str | None:
  '''Check if a configuration file is loaded in CANoe.
  Args:
      canoe_exe: The name of the CANoe executable.
  Returns:
      str | None: 
        - Returns the full path of the configuration file if loaded, otherwise None.
  '''
  
  # Check if the application is running  
  # if count_running_processes(canoe_exe) != 1:
  #   return None
  
  try:
    with canoe_application_context() as app:
      # Verificar si hay una configuración cargada
      name = app.Configuration.Name
      full_name = app.Configuration.FullName
      
      # Devolver el path completo solo si hay un nombre de configuración
      return full_name if name else None
          
  except pythoncom.com_error as e:
    # Error específico de COM
    #print(f"COM Error al acceder a CANoe: {e}")
    return None
  
  except Exception as e:
    # Otros errores
    #print(f"Error inesperado: {e}")
    return None
  
def some_measurement_running_optimized(canoe_exe: str) -> str | None:
  '''Check if a measurement is running in CANoe (optimized version).
  Combines both configuration check and measurement check in a single COM connection.'''
  
  try:
    with canoe_application_context() as app:
      # Verificar si hay configuración cargada
      config_name = app.Configuration.Name
      config_full_name = app.Configuration.FullName
      
      if not config_name:
        return None

      # Verificar si la medición está corriendo
      is_running = app.Measurement.Running
      return config_full_name if is_running else None
        
  except pythoncom.com_error as e:
    #print(f"COM Error: {e}")
    return None
  
  except Exception as e:
    #print(f"Error: {e}")
    return None

def is_measurement_running(canoe_exe: str) -> bool:
  '''Check if measurement is running
  Args:
    canoe_exe: The name of the CANoe executable.
    
  Returns:
    bool: True if the measurement is running, False otherwise.'''
  
  try:
    with canoe_application_context() as app:
       
      return app.Measurement.Running
        
  except pythoncom.com_error as e:
    #print(f"COM Error: {e}")
    return False
  
  except Exception as e:
    #print(f"Error: {e}")
    return False
    
def start_measurement2(cfg_id: str, cfg_path: str, canoe_exe: str, wit_ui: bool = False) -> str:
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
        return f'0000,{cfg_id} {cfg_path} measurement running'
      
  # Open CANoe application with the specified configuration file
  try:
    canoe_inst = CANoe()
  except Exception as e:
    return f'8110,{cfg_id} Impossible to load CANoe() instance'
  
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
    del canoe_inst
    return f'8111,{cfg_id} Impossible to open file: {cfg_path}'
  
  # Try to start measurment
  try:
    canoe_inst.start_measurement()
    del canoe_inst
    
  except Exception as e:
    del canoe_inst
    return f'8112,{cfg_id} Impossible to start measurement, file: {cfg_path}'
  
  # Done
  return f'0000,{cfg_id} {cfg_path} measurement running'

def start_measurement(cfg_id: str, cfg_path: str, canoe_exe: str, with_ui: bool = False) -> str:
  """
  Start measurement in Vector CANoe using COM API
  Args:
    cfg_id (str): Cfg ID
    cfg_path (str): Cfg file path
    with_ui (bool): True use GUI, otherwise hidden

  Returns:
    str: 0000,{cfg_id} {cfg_path} measurement running\n
    8110,{cfg_id} Impossible to start measurement, file: {cfg_path}\n
    8111,{cfg_id} Some error when opening file {cfg_path}
  """
  logger = logging.getLogger('start_measurement')
  
  try:
    with canoe_application_context() as app:
      
      logger.debug('Get meas and cfg')
      meas = app.Measurement
      cfg = app.Configuration

      target_cfg = os.path.abspath(cfg_path).lower()
      current_cfg = (cfg.FullName or "").lower()
      logger.debug(f'target: {target_cfg}, current: {current_cfg}')
      
      # Case 1: it's already running
      if meas.Running and current_cfg == target_cfg:
        logger.debug('Case 1: It is already running')
        return f'0000,{cfg_id} {cfg_path} measurement running'
      
      # Case 2: Other config is running, stop it!
      if meas.Running and current_cfg != target_cfg:
        logger.debug(f"⚠️ Measurement is running with: {cfg.FullName}, stopping")
        meas.Stop()
        sleep(1.0)
        logger.debug('Measurment stop!')

      # Case 3: Load new cfg file
      if current_cfg != target_cfg:
        logger.debug(f"🔄 Load new cfg: {cfg_path}")
        app.Visible = with_ui
        app.Open(cfg_path)
        
        sleep(2)
        logger.debug('Loaded')
                  
      # Start measurement
      if not meas.Running:
        logger.debug('Start measurment.')
        meas.Start()
        
        # Waiting measurment running
        for _ in range(20):
          logger.debug('Waiting measurement')
          
          if meas.Running:
            return f'0000,{cfg_id} {cfg_path} measurement running'
          sleep(0.5)
          
        # Impossible to start measurement
        logger.error("\n⛔ No se pudo arrancar la medición.")
        return f'8110,{cfg_id} Impossible to start measurement, file: {cfg_path}'

      
      return f'0000,{cfg_id} {cfg_path} measurement running'
                    
  except pythoncom.com_error as e:
    logger.error(f"COM Error: {e}")
    return f'8111,{cfg_id} Some error when opening file {cfg_path}'
  
  except Exception as e:
    logger.error(f"Error: {e}")
    return f'8111,{cfg_id} Some error when opening file {cfg_path}'
