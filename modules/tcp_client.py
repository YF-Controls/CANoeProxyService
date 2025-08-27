import socket
import logging

class TCPClient:
  """"TCP Client class
  """
  
  def __init__(self, host: str, port: int, timeout: float | None = None) :
    self.id = f'{host}:{port}'
    self.host = host
    self.port = port
    self.timeout = timeout
    self.socket = None
    self.logger = logging.getLogger('TCPClient')

  def __enter__(self):
    """Enter method for statment with
    """
    self.connect()
    return self
  
  
  def __exit__(self, exception_type, exception_value, exception_traceback):
    """Exit method for statment with
    """
    self.close()
    return False # Avoid to suprime exception
  
  
  def connect(self):
    """Establish the connection to TCP Server
    """
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.settimeout(self.timeout)
      self.socket.connect((self.host, self.port))
      self.logger.info(f'[{self.id}] connect: Connected to {self.host}:{self.port}')
            
    except socket.error:
      msg = f'[{self.id}] connect: socket error'
      self.logger.error(msg)
      raise ConnectionError(msg)
  
    except socket.timeout:
      msg = f'[{self.id}] connect: socket timeout'
      self.logger.error(msg)
      raise ConnectionError(msg)

    except socket.gaierror:
      msg = f'[{self.id}] connect: socket gaierror'
      self.logger.error(msg)
      raise ConnectionError(msg)
    
    except Exception as e:
      msg = f'[{self.id}] connect: Excpetion {e}'
      self.logger.error(msg)
      raise ConnectionError(msg)
    

  def send_message(self, message: str, response_timeout: float | None = 5):
    """Send message
    """
    if not self.socket:
      msg = f'[{self.id}] send_message: socket is None'
      self.logger.error(msg)
      raise ConnectionError(msg)
    
    try:
      self.socket.sendall(message.encode('utf-8'))
      self.logger.info(f'[{self.id}] send_message: data<{message}>')
      
      if response_timeout:
        self.socket.settimeout(response_timeout) # Set timeout
      
    except socket.error:
      msg = f'[{self.id}] send_message: socket error'
      self.logger.error(msg)
      raise ConnectionError(msg)
    
    except BrokenPipeError:
      msg = f'[{self.id}] send_message: broken pipe error'
      self.logger.error(msg)
      raise ConnectionError(msg)

    except ConnectionResetError:
      msg = f'[{self.id}] send_message: connection reset error'
      self.logger.error(msg)
      raise ConnectionError(msg)

    except Exception as e:
      msg = f'[{self.id}] send_message: Exception {e}'
      self.logger.error(msg)
      raise ConnectionError(msg)
    
      
  def receive_response(self, buffer_size: int = 1024) -> str:
    """Receive message
    """
    if not self.socket:
      msg = f'[{self.id}] receive_message: socket is None'
      self.logger.error(msg)
      raise ConnectionError(msg)
    
    try:
      response = self.socket.recv(buffer_size).decode('utf-8')
      self.logger.info(f'[{self.id}] receive_message: data<{response}>')
      return response
    
    except socket.timeout as e:
      msg = f'[{self.id}] receive_message: socket timeout'
      self.logger.error(msg)
      raise ConnectionError(msg)
    
    except BrokenPipeError:
      msg = f'[{self.id}] receive_message: broken pipe error'
      self.logger.error(msg)
      raise ConnectionError(msg)

    except ConnectionResetError:
      msg = f'[{self.id}] receive_message: connection reset error'
      self.logger.error(msg)
      raise ConnectionError(msg)

    except Exception as e:
      msg = f'[{self.id}] receive_message: Exception {e}'
      self.logger.error(msg)
      raise ConnectionError(msg)

 
  def close(self):
    """Close connection
    """
    if self.socket is None:
      return
    
    try:
      self.socket.close()
      self.logger.info(f'[{self.id}] close connection')
      
    except socket.error as e:
      msg = f'[{self.id}] receive_message: Exception {e}'
      self.logger.error(msg)
      

    except Exception as e:
      msg = f'[{self.id}] receive_message: Exception {e}'
      self.logger.error(msg)
      
    finally:
      self.socket = None
