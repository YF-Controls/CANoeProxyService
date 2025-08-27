import win32ts  # Para funciones de Terminal Services (WTS*)
import win32con
import win32process
import win32security  # Para manejar tokens de usuario
import win32api

def startProcess(path: str):
    try:
        # 1. Obtener la sesión activa del usuario actual
        session_id = win32ts.WTSGetActiveConsoleSessionId()
        
        # 2. Obtener el token del usuario de esa sesión
        user_token = win32ts.WTSQueryUserToken(session_id)
        
        # 3. Configurar cómo se mostrará la ventana
        startup_info = win32process.STARTUPINFO()
        startup_info.dwFlags = win32con.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = win32con.SW_SHOW  # Mostrar ventana normalmente
        
        # 4. Crear el proceso en la sesión del usuario
        process_info = win32process.CreateProcessAsUser(
            user_token,                # Token del usuario
            path,                      # Ruta del ejecutable
            None,                      # Argumentos (None para usar el string completo)
            None,                      # Atributos de proceso (seguridad)
            None,                      # Atributos de hilo (seguridad)
            False,                     # ¿Heredar handles? (False para seguridad)
            win32con.NORMAL_PRIORITY_CLASS,  # Prioridad
            None,                      # Entorno (None = heredar del padre)
            None,                      # Directorio de trabajo (None = mismo que padre)
            startup_info               # Configuración de inicio
        )
        
        print(f'Pid: {process_info[2]}')
        
        return process_info[2]  # Retorna el PID (process_info[2] = PID)
    
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        return None
      

if __name__ == '__main__':
  
  startProcess('C:\\Users\\cyanezf\\Downloads\\hercules_3-2-8.exe')