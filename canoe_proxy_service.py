# -*- coding: utf-8 -*-
# Service (UTF-8)
# System libraries
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import ctypes
import socket
import os
# User modules
from canoe_proxy_tcp_server import CANoeProxyTcpServer

##############################################################
# Class to be used as a Service
##############################################################
class CANoeProxyService(win32serviceutil.ServiceFramework):
  """Windows Service to handle Can Oe apps and communication
  """
  
  _svc_name_ = "CANoe Proxy Service"
  _svc_display_name_ = "CANoe Proxy Service"
  _svc_description_ = "Service for managing CANoe configurations and commands"
  _svc_deps = []  # Dependencias opcionales
  
  def __init__(self, args):
    """Costructor
    """
    # Service code
    win32serviceutil.ServiceFramework.__init__(self, args)
    self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    #socket.setdefaulttimeout(60.0) # Used to connect with WSM
    # Socket is commented because timed out with tcp server.
    
    # User code
    # Admin
    self.is_admin: bool = self.check_admin()
    # Service arguments
    self.config_path: str = ''
    
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
    
    # Init server instance
    self.setup_service_arguments()
    self.server = CANoeProxyTcpServer(self.config_path)
    self.server.start()

  def check_admin(self) -> bool:
    """Check admin
    """
    try:
      isAdmin: bool = ctypes.windll.shell32.IsUserAnAdmin() != 0
      if isAdmin:
        servicemanager.LogInfoMsg('Service is running with admin privileges')
      else:
        servicemanager.LogWarningMsg('Service is not running with admin privileges')
        
      return isAdmin
    
    except Exception as e:
      servicemanager.LogErrorMsg(f'Error checking admin privileges: {e}')
      return False
    
  def setup_service_arguments(self):
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
    
    # Check path
    if not self.config_path:
      self.config_path = r'c:\CANoeProxyService\config.json'
      servicemanager.LogWarningMsg(f'No configuration file specified, load default: {self.config_path}')
    
    if not os.path.isfile(self.config_path):
      servicemanager.LogErrorMsg(f'Configuration file does not exist: {self.config_path}')
      
    else:
      servicemanager.LogInfoMsg(f"Configuration file specified: {self.config_path}")  
    
  

  
  
##############################################################
# Main call
##############################################################
if __name__ == '__main__':
  
  '''
  Open a command prompt as administrator and run:
  
  python canoe_proxy_service.py install"
  python canoe_proxy_service.py start
  python canoe_proxy_service.py status
  
  To stop the service:
  python canoe_proxy_service.py remove
  '''
  
  win32serviceutil.HandleCommandLine(CANoeProxyService)
  