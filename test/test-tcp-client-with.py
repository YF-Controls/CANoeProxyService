from datetime import datetime
from modules.tcp_client import TCPClient

if __name__ == '__main__':
  
  
  while True:
    
    print(datetime.now().isoformat())
    
    try:
      with TCPClient('localhost', 5000) as client:
        
        message = datetime.now().isoformat()
        client.send_message(message + '\n', None)
        print(message)
        
        response = client.receive_response()
        print(f'r: <{response}>')
        
        if response == '':
          raise ConnectionError('Respuesta vacía')
        
        
        continue
    
    except ConnectionError as e:
      print(f'Error de conexión: {e}')
    
    except TimeoutError as e:
      print(f'Error de tiempo: {e}')
    
    except Exception as e:
      print(f'Error inesperado: {e}')
    
      
    print(datetime.now().isoformat())

