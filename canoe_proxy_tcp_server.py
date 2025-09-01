# System libraries
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
from modules.util.file_util import check_file
from modules.models.config_model import ConfigModel
from modules.util.process_util import *
from modules.util.string_util import *
from modules.vector_canoe import *
from modules.models.canoe_model import CanOeCfgModel

##############################################################
# Class to handle TCP Server and Process (Apps)
##############################################################
class CANoeProxyTcpServer:
  
  def __init__ (self, config_path: str):
    """Cosntructor
    """
    
    # Init system variables
    self.config = None
    self.logger = None
    
    # Setup
    self.setup_config(config_path)
    self.setup_logger()

    # Define server config
    self.server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 1 enables SO_REUSEADDR
    self.clients = {}
      
  def start (self):
    """Start TCP Server
    """
    # host = 0.0.0.0 listen all networks
    # host = 127.0.0.1 listen local connection
    # host = x.x.x.x listen in specific address
    
    self.server_socket.bind((self.config.service.host, self.config.service.port))
    self.server_socket.listen(5) # Listen until 5 clients
    self.isRunning = True
    self.log_info(f'TCP Server is listening on {self.config.service.host}:{self.config.service.port}')
    
    try:
      while self.isRunning:
        client_socket, client_address = self.server_socket.accept()
        thread = threading.Thread(target=self.client_handler, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()
    
    except Exception as e:
      self.log_error(f'TCP Server error in start loop: {e}')
    finally:
      self.server_socket.close()
    
  def client_handler (self, client_socket, client_address):
    """Handle client connection in an isolated thread
    """
        
    client_id = f'{client_address[0]}:{client_address[1]}' # Get client id
    self.clients[client_id] = client_socket # Add socket to client
    self.log_info(f'Client[{client_id}] connected from {client_address[0]}:{client_address[1]}')
    
    try:
      while True:
        # Receive command from PLC
        received_data = client_socket.recv(1024).decode('utf-8')
        args = clear_spaeces(received_data).split(' ')
        args_nr= len(args) - 1
        command = args[0]
        self.log_info(f'Client[{client_id}] received command: {command}')
                
        # Raw disconnection
        if not command:
          self.log_info(f'Client[{client_id}] command: No command, disconnecting') # Log
          break # Exit loop
        
        
        
        
        
        # Get CANoe application status
        elif command == 'status': # No parameters
          # PLC command: status
          # Service response:
          # 0000,{cfg_id} {cfg_file} measurement running
          # 7000,{canoe_exe} closed
          # 7001,No cfg file loaded
          # 7002,{cfg_file} waiting to start measurement
          # 8000,Too many open {canoe_exe} instances
                
          # Count processes
          count = count_running_processes(self.config.canOe.exe)
          
          # Check status
          if count < 1:
            response = f'7000,{self.config.canOe.exe} closed'
            client_socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
        
          if count > 1:
            response = f'8000,Too many open {self.config.canOe.exe} instances'
            client_socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # Read cfg path
          cfg_path = some_cfg_loaded(self.config.canOe.exe)
            
          if cfg_path is None:
            response = f'7001,No cfg file loaded' 
            client_socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # Read cfg id
          cfg_id = self.config.canOe.get_cfg_id_by_path(cfg_path)
            
          if cfg_id is None:
            cfg_id = '???'
            
          if is_measurement_running(self.config.canOe.exe):
            response = f'0000,{cfg_id} {cfg_path} measurement running'
            
          else:
            response = f'7002,{cfg_id} {cfg_path} waiting to start measurement'
          
          # Send response
          client_socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
          
        
        
        
        
        
        # Start CANoe application
        elif command == 'start': # parameters: cfg_id
          # PLC command: start {cfg_id}
          # Service response: 
          # 0000,{cfg_id} {cfg_file} measurement running
          # 8100,Missing parameters
          # 8101,Too many parameters
          # 8102,Unknown cfg_id: {cfg_id}
          # 8110,{cfg_id} Impossible to start measurement, file: {cfg_path}
          # 8111,{cfg_id} Some error when opening file {cfg_path}
          
          # No arguments
          if args_nr < 1:
            response = '8100,Missing parameters'
            client_socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
        
          # Too many arguments
          if args_nr > 1:
            response = '8101,Too many parameters'
            client_socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
        
          # Cfg_id argument
          cfg_id = args[1] # Get cfg_id
          cfg: CanOeCfgModel = self.config.canOe.get_cfg_by_id(cfg_id)
          
          if cfg is None:
            response = f'8102,Unknown cfg_id: {cfg_id}'
            client_socket.send(response.encode('utf-8'))
            self.log_info(f'Client[{client_id}] response: {response}')
            continue
          
          # Start application
          response = start_measurement(cfg_id, cfg.path, self.config.canOe.exe, True)
          client_socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
          
        
        
        
        elif command == 'close': # No parameters
          # PLC command: close
          # Service response:
          # 0000,{canoe.exe} closed!
          # 8200,Impossible to close {canoe_exe}. Force manually!
          
          if kill_process(self.config.canOe.exe):
            response = f'0000,{self.config.canOe.exe} closed!'
          
          else:
            response = f'8200,Impossible to close {self.config.canOe.exe}. Force manually!'
          
          client_socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
        
        
        
        
        
        elif command == 'help': # No parameters
          # PLC command: help
          # Service response:
          # 0000,Available commands: status, start {cfg_id}, close, help
          
          response = '0000,Available commands: status, start {cfg_id}, close, help'
          client_socket.send(response.encode('utf-8'))
          self.log_info(f'Client[{client_id}] response: {response}')
          continue
          
        # Unknown command                
        else:
          # 80FF,Error: Unknown command
          response = '8FFF,Unknown command'
          client_socket.send(response.encode('utf-8'))
          self.log_warning(f'Client[{client_id}] response: {response}')
          continue
        
    except Exception as e:
      self.log_error(f'Client[{client_id}] error: {e}')
    
    finally:
      client_socket.close()
      del self.clients[client_id]
      self.log_info(f'Client[{client_id}] disconnected!')

  def setup_config(self, config_path: str):
    """Load configuration from file
    """
    try:
      self.config = ConfigModel.from_file(config_path)
      
    except Exception as e:
      exit(f'Impossible to load config file: {config_path}\nException: {e}')
    
  def setup_logger(self):
    
    try:
      self.logger = logging.getLogger(self.__class__.__name__)
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
      
    except Exception as e:
      
      self.logger = logging.getLogger(self.__class__.__name__)
      
      logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s [%(levelname)-8s] %(message)-80s [%(name)s , %(funcName)s , %(lineno)d]',
        handlers=[
          logging.handlers.RotatingFileHandler(
            filename= r"C:\CanOeProxy.log",
            maxBytes=10485760,  # 10 MB
            backupCount=20
          )
        ]
      )
  
  def log_debug(self, message):
    """Log debug message
    """
    self.logger.debug(message)
        
  def log_info(self, message):
    """Log info message
    """
    self.logger.info(message)
          
  def log_warning(self, message):
    """Log warning message
    """
    self.logger.warning(message)
          
  def log_error(self, message):
    """Log error message
    """
    self.logger.error(message)
  
  def log_critical(self, message):  
    """Log critical message
    """
    self.logger.critical(message)
    
  
  