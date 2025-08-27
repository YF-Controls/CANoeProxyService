import socket
import threading
import subprocess
import logging
import time
import select
from typing import Optional, Tuple, List

class TCPProxyServer:
  '''Servidor proxy TCP que maneja conexiones de clientes y reenvía comandos a un servidor destino.
  Permite iniciar aplicaciones, verificar su estado, conectar/desconectar al servidor destino, 
  y enviar comandos con timeout configurable.
  '''
  
  def __init__(self, host: str = '0.0.0.0', port: int = 8888):
    '''Inicializa el servidor proxy TCP.
    Args:
      host (str): Dirección IP en la que el servidor escucha.
      port (int): Puerto en el que el servidor escucha.
    '''
    
    self.host = host
    self.port = port
    self.running = False
    self.server_socket = None
    self.target_connection = None
    self.target_address = None
    self.running_apps = {}
    self.connection_status = "DISCONNECTED"
    
    logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s'
    )
    self.logger = logging.getLogger(__name__)
  
  
  def cmd_start_application(self, app_name: str) -> bool:
    '''Inicia una aplicación externa.
    Args:
      app_name (str): Nombre o ruta de la aplicación a iniciar.
    Returns:
      bool: True si la aplicación se inició correctamente, False en caso contrario.
    '''
    
    try:
      process = subprocess.Popen(app_name, shell=True)
      self.running_apps[app_name] = process
      self.logger.info(f"Aplicación '{app_name}' iniciada con PID {process.pid}")
      return True
    except Exception as e:
      self.logger.error(f"Error al iniciar aplicación '{app_name}': {e}")
      return False
  
  def cmd_check_application_status(self, app_name: str) -> str:
    if app_name in self.running_apps:
      process = self.running_apps[app_name]
      if process.poll() is None:
        return f"RUNNING (PID: {process.pid})"
      else:
        return "STOPPED"
    return "NOT_STARTED"
  
  def cmd_connect_to_target(self, target_host: str, target_port: int) -> bool:
    try:
      if self.target_connection:
        self.target_connection.close()
      
      target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      target_socket.settimeout(5)
      target_socket.connect((target_host, target_port))
      
      self.target_connection = target_socket
      self.target_address = (target_host, target_port)
      self.connection_status = f"CONNECTED_TO_{target_host}:{target_port}"
      self.logger.info(f"Conectado a servidor destino {target_host}:{target_port}")
      return True
    except Exception as e:
      self.logger.error(f"Error al conectar con destino {target_host}:{target_port}: {e}")
      return False
  
  def disconnect_from_target(self):
    if self.target_connection:
      try:
        self.target_connection.close()
        self.logger.info(f"Desconectado de servidor destino {self.target_address}")
      except:
        pass
      finally:
        self.target_connection = None
        self.target_address = None
        self.connection_status = "DISCONNECTED"
  
  def cmd_send_to_target_with_timeout(self, command: str, timeout: float) -> Optional[str]:
    
    if not self.target_connection:
      return None
    
    try:
      self.target_connection.sendall(command.encode('utf-8'))
      self.logger.info(f"Comando enviado al destino: '{command}' (timeout: {timeout}s)")
      
      start_time = time.time()
      response_data = b""
      
      self.target_connection.settimeout(timeout)
      
      try:
        while True:
          if time.time() - start_time > timeout:
            self.logger.warning(f"Timeout de {timeout}s alcanzado para comando: '{command}'")
            return f"TIMEOUT_ERROR: No se recibió respuesta en {timeout} segundos"
          
          data = self.target_connection.recv(4096)
          if not data:
            break
          
          response_data += data
          
          time.sleep(0.1)
          
          ready = select.select([self.target_connection], [], [], 0.1)
          if not ready[0]:
            break
            
      except socket.timeout:
        self.logger.warning(f"Socket timeout después de {timeout}s para comando: '{command}'")
        if response_data:
          return f"PARTIAL_RESPONSE: {response_data.decode('utf-8', errors='ignore')}"
        else:
          return f"TIMEOUT_ERROR: No se recibió respuesta en {timeout} segundos"
      
      except Exception as e:
        self.logger.error(f"Error durante recepción con timeout: {e}")
        if response_data:
          return f"PARTIAL_RESPONSE_WITH_ERROR: {response_data.decode('utf-8', errors='ignore')} (Error: {str(e)})"
        else:
          return f"ERROR: {str(e)}"
      
      self.target_connection.settimeout(5)
      
      if response_data:
        return response_data.decode('utf-8')
      else:
        return "NO_RESPONSE"
        
    except Exception as e:
      self.logger.error(f"Error al enviar comando al destino: {e}")
      return f"ERROR: {str(e)}"
  
  def get_detailed_status(self) -> str:
    status_lines = []
    
    if self.target_connection:
      status_lines.append(f"CONEXION_DESTINO: {self.connection_status}")
      status_lines.append(f"DESTINO_ACTUAL: {self.target_address[0]}:{self.target_address[1]}")
    else:
      status_lines.append("CONEXION_DESTINO: DESCONECTADO")
      status_lines.append("DESTINO_ACTUAL: NINGUNO")
    
    if self.running_apps:
      apps_status = []
      for app_name, process in self.running_apps.items():
        status = "EJECUTANDOSE" if process.poll() is None else "DETENIDA"
        pid = process.pid if process.poll() is None else "N/A"
        apps_status.append(f"{app_name} -> {status} (PID: {pid})")
      status_lines.append("APLICACIONES: " + "; ".join(apps_status))
    else:
      status_lines.append("APLICACIONES: NINGUNA")
    
    status_lines.append(f"SERVIDOR_PROXY: ACTIVO en {self.host}:{self.port}")
    status_lines.append(f"CLIENTES_CONECTADOS: {threading.active_count() - 2}")
    
    return "\n".join(status_lines)
  
  def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
    self.logger.info(f"Conexión establecida con {client_address}")
    
    try:
      while True:
        data = client_socket.recv(1024).decode('utf-8').strip()
        if not data:
          break
        
        self.logger.info(f"Comando recibido de {client_address}: {data}")
        
        response = self.process_command(data, client_address)
        
        client_socket.sendall(response.encode('utf-8'))
        
    except ConnectionResetError:
      self.logger.info(f"Conexión cerrada por {client_address}")
    except Exception as e:
      self.logger.error(f"Error con cliente {client_address}: {e}")
    finally:
      client_socket.close()
      self.logger.info(f"Conexión terminada con {client_address}")
  
  def process_command(self, command: str, client_address: Tuple[str, int]) -> str:
    parts = command.split()
    if not parts:
      return "ERROR: Comando vacío"
    
    cmd = parts[0].lower()
    
    if cmd == "start" and len(parts) > 1:
      app_name = " ".join(parts[1:])
      success = self.cmd_start_application(app_name)
      return "APPLICATION_STARTED" if success else "APPLICATION_START_FAILED"
    
    elif cmd == "status":
      if len(parts) > 1:
        app_name = " ".join(parts[1:])
        status = self.cmd_check_application_status(app_name)
        return f"APP_STATUS: {status}"
      else:
        return self.get_detailed_status()
    
    elif cmd == "connect" and len(parts) == 3:
      try:
        target_host = parts[1]
        target_port = int(parts[2])
        success = self.cmd_connect_to_target(target_host, target_port)
        return "CONNECTED" if success else "CONNECTION_FAILED"
      except ValueError:
        return "ERROR: Puerto inválido"
    
    elif cmd == "cmd-to-destination" and len(parts) > 2:
      if not self.target_connection:
        return "ERROR: No conectado a servidor destino"
      
      try:
        timeout = float(parts[1])
        if timeout <= 0:
          timeout = 5.0
        elif timeout > 600.0:
          timeout = 600.0
        
        sub_command = " ".join(parts[2:])
        
        response = self.send_to_target_with_timeout(sub_command, timeout)
        
        if response:
          return f"{self.target_address[0]}:{response}"
        return "ERROR: No response from target"
        
      except ValueError:
        return "ERROR: Timeout debe ser un número válido"
      except Exception as e:
        return f"ERROR: {str(e)}"
    
    elif cmd == "disconnect":
      self.disconnect_from_target()
      return "DISCONNECTED_FROM_TARGET"
    
    else:
      return "ERROR: Comando no reconocido. Comandos válidos: start, status, connect, cmd-to-destination, disconnect"
  
  def start_server(self):
    try:
      self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.server_socket.bind((self.host, self.port))
      self.server_socket.listen(5)
      
      self.running = True
      self.logger.info(f"Servidor proxy iniciado en {self.host}:{self.port}")
      
      while self.running:
        try:
          client_socket, client_address = self.server_socket.accept()
          
          client_thread = threading.Thread(
            target=self.handle_client,
            args=(client_socket, client_address),
            daemon=True
          )
          client_thread.start()
          
        except KeyboardInterrupt:
          self.logger.info("Servidor detenido por el usuario")
          break
        except Exception as e:
          self.logger.error(f"Error al aceptar conexión: {e}")
    
    except Exception as e:
      self.logger.error(f"Error al iniciar servidor: {e}")
    finally:
      self.stop_server()
  
  def stop_server(self):
    self.running = False
    self.disconnect_from_target()
    
    for app_name, process in self.running_apps.items():
      try:
        process.terminate()
        self.logger.info(f"Aplicación '{app_name}' terminada")
      except:
        pass
    
    if self.server_socket:
      try:
        self.server_socket.close()
      except:
        pass
    
    self.logger.info("Servidor proxy detenido")

if __name__ == "__main__":

  proxy = TCPProxyServer('0.0.0.0', 8888)
  
  try:
    server_thread = threading.Thread(target=proxy.start_server, daemon=True)
    server_thread.start()
    
    print("Servidor proxy iniciado. Presiona Ctrl+C para detener.\n")
    print("Para probar:")
    print("1. Servidor destino: python script.py destination")
    print("2. Cliente interactivo: python script.py client\n")
    print("Nuevo formato para cmd-to-destination:")
    print("  cmd-to-destination <timeout> <comando>")
    print("  Ejemplo: cmd-to-destination 2.5 ping")
    print("  Ejemplo: cmd-to-destination 1.0 slow")
    
    while True:
      time.sleep(1)
      
  except KeyboardInterrupt:
    print("\nDeteniendo servidor proxy...")
    proxy.stop_server()
  