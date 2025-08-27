# -*- coding: utf-8 -*-
# Service (UTF-8)
# Service libraries
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import ctypes
import os
# Datetime libraries
from datetime import datetime
import time
# Communication libraries
import socket
import threading
# Logging libraries
import logging
import logging.handlers
# User modules
from modules.models.config_model import ConfigModel
from modules.tcp_client import TCPClient
from modules.util.file_util import check_file
from modules.util.process_util import *
from modules.util.string_util import *
from modules.vector_canoe import *

##############################################################
# Class to handle TCP Server and Process (Apps)
##############################################################
class CANoeTcpProxyServer:
  
  def __init__ (self, config: ConfigModel):
    """Cosntructor
    """
    self.config = config
    self.server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 1 enables SO_REUSEADDR
    self.clients = {}
    self.logger = logging.getLogger(config.service.name)
      
  def start (self):
    """Start TCP Server
    """
    # host = 0.0.0.0 listen all networks
    # host = 127.0.0.1 listen local connection
    # host = x.x.x.x listen in specific address
    
    self.server_socket.bind((self.config.host, self.config.port))
    self.server_socket.listen(5) # Listen until 5 clients
    self.isRunning = True
    self.log_info(f'TCP Server is starting on {self.config.host}:{self.config.port}')
    
    try:
      while self.isRunning:
        client_socket, addr = self.server_socket.accept()
        thread = threading.Thread(target=self.client_handler, args=(client_socket, addr))
        thread.daemon = True
        thread.start()
    
    except Exception as e:
      self.log_error(f'TCP Server error in start loop: {e}')
    finally:
      self.server_socket.close()
    
  def client_handler (self, socket, address):
    """Handle client connection in an isolated thread
    """
    client_id = f'{address[0]}:{address[1]}'
    self.clients[client_id] = socket
    self.log_info(f'Client[{client_id}] connected from {address[0]}:{address[1]}')
    
    try:
      while True:
        # Receive command from PLC
        received_data = socket.recv(1024).decode('utf-8')
        args = clear_spaeces(received_data).split(' ')
        args_nr= len(args) - 1
        command = args[0]
        servicemanager.LogInfoMsg(f'Client[{client_id}] command: {command}')
        
        # Raw disconnection
        if not command:
          self.log_info(f'Client[{client_id}] command: No command, disconnecting') # Log
          break # Exit loop
        
        # Parsing error
        elif not args:
          response = '8FFF,Unknown command'
          socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
          
        # Get CANoe application status
        elif command == 'app-status': # No parameters
          # PLC command: app-status
          # Service response: 0000,{cfg.id} in measurement
          # Service response: 8010,No cfg file in measurement
          # Service response: 8011,unknown cfg file in measurement: {cfg_path}
          
          # Get configuration file loaded
          cfg_path = some_measurement_running(self.config.canOe.exe)
          
          if cfg_path is None:
            response = '8010,No cfg file in measurement'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # Get configuration id
          cfg_id = self.config.canOe.get_cfg_id_by_path(cfg_path)
          
          if cfg_id is None:
            response = f'8011,Unknown cfg file in measurement: {cfg_path.lower()}'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # All ok
          response = f'0000,{cfg_id} in measurement'
          socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
          
          
          
        # Start CANoe application
        elif command == 'start-app': # parameters: cfg_id
          # PLC command: start-app {cfg_id}
          # Service response: 0000,{cfg.id} in measurement
          # Service response: 8000,Missing parameters
          # Service response: 8001,Too many parameters
          # Service response: 8002,Unknown cfg_id {cfg_id}
          # Service response: 8003,Impossible to start {cfg_id}
          
          # No arguments
          if args_nr < 1:
            response = '8000,Missing parameters'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
        
          # Too many arguments
          if args_nr > 1:
            response = '8001,Too many parameters'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
        
          # Cfg_id argument
          cfg_id = args[1] # Get cfg_id
          cfg_path = self.config.canOe.get_cfg_path_by_id(cfg_id) # Get cfg_path
          
          if cfg_path is None:
            response = f'8002,Unknown cfg_id {cfg_id}'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # Start application
          done = start_app(cfg_path, self.config.canOe.exe)
          
          if not done:
            response = f'8003,Impossible to start {cfg_id}'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # Done
          response = f'0000,{cfg_id} in measurement'
          socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
              
        
        # Execute CANoe application command
        elif command == 'canoe-cmd': # parameters: <timeout> <CanOeCommand> <CanOeParameter>
          # PLC command: canoe-cmd <timeout> <CanOeCommand> <CanOeParameter>
          # Service response: 0000,{CanOeResponse}
          # Service response: 8000,Missing parameters
          # Service response: 8001,Too many parameters
          # Service response: 8010,No cfg file in measurement
          # Service response: 8011,Unknown cfg file in measurement: {cfg_path}
          # Service response: 8040,Connection error to CANoe application
          # Service response: 8041,Timeout error from CANoe application
          # Service response: 8042,Unexpected error with CANoe application
          
          # Missing parameters
          if args_nr < 3:
            response = '8000,Missing parameters'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
            
          # Too many arguments  
          if args_nr > 3:
            response = '8001,Too many parameters'          
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
                    
          # Get cfg_path
          cfg_path = some_measurement_running(self.config.canOe.exe)
            
          if cfg_path is None:
            response = '8010,No cfg file in measurement'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
            
          # Get cfg_id
          cfg_id = self.config.canOe.get_cfg_id_by_path(cfg_path)
          
          if cfg_id is None:
            response = f'8011,Unknown cfg file in measurement: {cfg_path.lower()}'
            socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
                    
          # Get arguments
          canoe_timeout = str_to_float(args[1], 60.0) # Get CanOeTimeout
          canoe_cmd = args[2] # Get CanOeCommand
          canoe_arg = args[3] # Get CanOeParameter
          # Set CANoe command
          canoe_message = f'{canoe_cmd} {canoe_arg}'
          canoe_cfg = self.config.canOe.get_cfg_by_id(cfg_id)
          canoe_host = canoe_cfg.host
          canoe_port = canoe_cfg.port
          
          # Send can oe command and wait response
          try:
            with TCPClient(canoe_host, canoe_port) as canoe_client:
              
              canoe_client.send_message(canoe_message, canoe_timeout)
              canoe_response = canoe_client.receive_response()
              
              if canoe_response == '':
                raise ConnectionError('Empty response')
              
          except ConnectionError as e:
            response = f'8040,Connection error to CANoe application'
            socket.send(response.encode('utf-8'))
            self.log_error(f'Client[{client_id}] response: {response}')
            continue
            
          except TimeoutError as e:
            response = f'8041,Timeout error from CANoe application'
            socket.send(response.encode('utf-8'))
            self.log_error(f'Client[{client_id}] response: {response}')
            continue
            
          except Exception as e:
            response = f'8042,Unexpected error with CANoe application'
            socket.send(response.encode('utf-8'))
            self.log_error(f'Client[{client_id}] response: {response}')
            continue
          
          # Process response
          response = f'0000,{canoe_response}'
          socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
          
                    
        # Unknown command                
        else:
          # 80FF,Error: Unknown command
          response = '8FFF,Unknown command'
          socket.send(response.encode('utf-8'))
          self.log_warning(f'Client[{client_id}] response: {response}')
          continue
        
    except Exception as e:
      servicemanager.LogErrorMsg(f'Client[{client_id}] error: {e}')
    
    finally:
      socket.close()
      del self.clients[client_id]
      servicemanager.LogInfoMsg(f'Client[{client_id}] disconnected!')

  def log_debug(self, message):
    """Log debug message
    """
    self.logger.debug(message)
    if self.config.log.printToEventViewer:
      servicemanager.LogInfoMsg(message)
    
  def log_info(self, message):
    """Log info message
    """
    self.logger.info(message)
    if self.config.log.printToEventViewer:
      servicemanager.LogInfoMsg(message)
      
  def log_warning(self, message):
    """Log warning message
    """
    self.logger.warning(message)
    if self.config.log.printToEventViewer:
      servicemanager.LogWarningMsg(message)
      
  def log_error(self, message):
    """Log error message
    """
    self.logger.error(message)
    if self.config.log.printToEventViewer:
      servicemanager.LogErrorMsg(message) 
  
  def log_critical(self, message):  
    """Log critical message
    """
    self.logger.critical(message)
    if self.config.log.printToEventViewer:
      servicemanager.LogErrorMsg(message)
  
    
##############################################################
# Class to be used as a Service
##############################################################
class CANoeProxyService(win32serviceutil.ServiceFramework):
  """Windows Service to handle Can Oe apps and communication
  """
  
  _svc_name_ = "Can Oe Handler Service"
  _svc_display_name_ = "Can Oe Handler Service"
  _svc_description_ = "Windows service to handle Can Oe apps and communication"
  _svc_deps = []  # Dependencias opcionales
  
  def __init__(self, args):
    """Costructor
    """
    # Service code
    win32serviceutil.ServiceFramework.__init__(self, args)
    self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    
    # User code
    self.config_path = None
    self.config = None
    self.logger = None
    self.is_admin = self.check_admin()
  
  def SvcStop(self):
    """Service Stop
    """
    # System
    self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
    win32event.SetEvent(self.hWaitStop)
    
    # User
    servicemanager.LogWarningMsg('Service is stopping... (closing server socket)')
    try:
      self.server.server_socket.close()
      servicemanager.LogInfoMsg('Server socket closed successfully!')
    except Exception as e:
      servicemanager.LogErrorMsg(f'Error closing server socket: {e}')

  def SvcDoRun(self):
    """Service Run
    """
    
    # Register service start
    servicemanager.LogMsg(
      servicemanager.EVENTLOG_INFORMATION_TYPE,
      servicemanager.PYS_SERVICE_STARTED,
      (self._svc_name_, '')
    )
    
    # Load configuration
    self.setup_arguments()
    
    if not self.setup_config():
      return
    
    self.setup_logger()
    
    # Init server instance
    self.server = CANoeTcpProxyServer(self.config)
    self.server.start()

  def check_admin(self):
    """Check admin
    """
    try:
      isAdmin = ctypes.windll.shell32.IsUserAnAdmin() != 0
      if isAdmin:
        servicemanager.LogInfoMsg('Service is running with admin privileges')
      else:
        servicemanager.LogWarningMsg('Service is not running with admin privileges')
        
    except Exception as e:
      servicemanager.LogErrorMsg(f'Error checking admin privileges: {e}')
      return False
    
  def setup_arguments(self):
    """Parse service arguments
    """
    
    # Arguments are in sys.argv when the service is started
    args = sys.argv[1:]  # Exclude script name
    
    for i, arg in enumerate(args):
      if arg in ['-c', '--config', '/config'] and i + 1 < len(args):
        self.config_path = args[i + 1]
        break
      elif arg.startswith('config='):
        self.config_path = arg.split('=', 1)[1]
    
    # Valor por defecto si no se especifica
    if not self.config_path:
      self.config_path = r"C:\CanOeService\config.json"
      servicemanager.LogInfoMsg(f"No configuration file specified, using default: {self.config_path}")
    else:
      servicemanager.LogInfoMsg(f"Configuration file specified: {self.config_path}")
  
  def setup_config(self):
    """Load configuration from file
    """
    try:
      self.config = ConfigModel.from_file(self.config_path)
      servicemanager.LogInfoMsg(f"Configuration file {self.config_path} loaded successfully!")
      return True
    
    except Exception:
      servicemanager.LogErrorMsg(f"Service could not start due to missing or corrupted configuration file: {self.config_path}")
      return False
     
  def setup_logger(self):
    
    try:
      self.logger = logging.getLogger(self._svc_name_)
      log_handlers = [] # List of log handlers
      
      # Create log directory if not exists
      check_file(self.config.log.filePath)
      
      # Optional: show log messages in console
      if self.config.log.printToConsole:
        log_handlers.append(logging.StreamHandler())
        
      # Mandatory: write log messages to file
      log_handlers.append(logging.handlers.RotatingFileHandler(
        filename= self.config.log.filePath,
        maxBytes=self.config.log.maxSize,
        backupCount=self.config.log.maxFiles
      ))
      
      # Set log configuration
      logging.basicConfig(
        level = self.config.log.level,
        format = self.config.log.format,
        handlers= log_handlers)
      
      # Log message to indicate logger setup
      servicemanager.LogInfoMsg(f"Logger setup complete with file: {self.config.log.filePath}")
      
    except Exception as e:
      servicemanager.LogErrorMsg(f"Error setting up logger: {e}")
      self.logger = logging.getLogger(self._svc_name_)
      logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s [%(levelname)-8s] %(message)-80s [%(name)s , %(funcName)s , %(lineno)d]',
        handlers=[
          logging.handlers.RotatingFileHandler(
            filename= r"C:\CanOeService.log",
            maxBytes=10485760,  # 10 MB
            backupCount=20
          )
        ]
      )

  
  
  
##############################################################
# Main call
##############################################################
if __name__ == '__main__':
  
  '''
  Open a command prompt as administrator and run:
  
  python can_oe_service.py install --config "C:\CanOeService\config.json"
  python can_oe_service.py start
  python can_oe_service.py status
  
  To stop the service:
  python can_oe_service.py remove
  '''
  
  win32serviceutil.HandleCommandLine(CANoeProxyService)
  