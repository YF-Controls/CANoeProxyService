# -*- coding: utf-8 -*-
# Service (UTF-8)
# System libraries
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import ctypes
# User modules
from canoe_proxy_tcp_server import CANoeProxyTcpServer

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
    
    # Valor por defecto si no se especifica
    if not self.config_path:
      self.config_path = r"C:\config.json"
      servicemanager.LogInfoMsg(f"No configuration file specified, using default: {self.config_path}")
    else:
      servicemanager.LogInfoMsg(f"Configuration file specified: {self.config_path}")
  

  
  
##############################################################
# Main call
##############################################################
if __name__ == '__main__':
  
  '''
  Open a command prompt as administrator and run:
  
  python can_oe_service.py install --config "C:\<folder-path>\config.json"
  python can_oe_service.py start
  python can_oe_service.py status
  
  To stop the service:
  python can_oe_service.py remove
  '''
  
  win32serviceutil.HandleCommandLine(CANoeProxyService)
  