import psutil
import os
import sys
import time
import ctypes
from typing import List, Union

def es_admin() -> bool:
    """Verifica si el script se ejecuta con privilegios de administrador"""
    try:
        return os.getuid() == 0  # Linux/Mac
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # Windows

def solicitar_elevacion():
    """Solicita elevación de privilegios en Windows"""
    if sys.platform == 'win32' and not es_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def matar_proceso(pid: int, timeout: float = 3.0) -> bool:
    """
    Intenta terminar un proceso primero suavemente y luego forzosamente
    
    Args:
        pid: ID del proceso
        timeout: Tiempo de espera antes de matar (segundos)
    
    Returns:
        True si el proceso fue terminado, False si no
    """
    try:
        proc = psutil.Process(pid)
        nombre = proc.name()
        
        print(f"Intentando terminar proceso {pid} ({nombre})...")
        
        # 1. Intento de terminación suave
        proc.terminate()
        try:
            proc.wait(timeout=timeout)
            print(f"Proceso {pid} ({nombre}) terminado correctamente")
            return True
        except psutil.TimeoutExpired:
            print(f"El proceso {pid} no respondió a terminate, intentando kill...")
        
        # 2. Terminación forzosa
        proc.kill()
        try:
            proc.wait(timeout=timeout)
            print(f"Proceso {pid} ({nombre}) terminado forzosamente")
            return True
        except psutil.TimeoutExpired:
            print(f"No se pudo terminar el proceso {pid} ({nombre})")
            return False
            
    except psutil.NoSuchProcess:
        print(f"El proceso {pid} ya no existe")
        return True
    except psutil.AccessDenied:
        print(f"Acceso denegado al proceso {pid}. Se requieren privilegios de administrador")
        return False

def matar_procesos_por_nombre(nombre_proceso: str, timeout: float = 3.0) -> List[int]:
    """
    Busca y mata todos los procesos con un nombre específico
    
    Args:
        nombre_proceso: Nombre del ejecutable (ej. "chrome.exe")
        timeout: Tiempo de espera por proceso
    
    Returns:
        Lista de PIDs terminados
    """
    pids_terminados = []
    nombre_proceso = nombre_proceso.lower()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == nombre_proceso:
                pid = proc.info['pid']
                if matar_proceso(pid, timeout):
                    pids_terminados.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return pids_terminados

if __name__ == "__main__":
    # Solicitar elevación si no somos admin
    if not es_admin():
        print("Se requieren privilegios de administrador")
        solicitar_elevacion()
    else:
        print("Ejecutando con privilegios de administrador")
    
    # Ejemplo de uso
    while True:
        print("\n1. Matar proceso por PID")
        print("2. Matar todos los procesos por nombre")
        print("3. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            try:
                pid = int(input("Ingrese el PID del proceso: "))
                matar_proceso(pid)
            except ValueError:
                print("Error: Ingrese un número válido")
        elif opcion == "2":
            nombre = input("Ingrese el nombre del proceso (ej. chrome.exe): ")
            terminados = matar_procesos_por_nombre(nombre)
            print(f"Procesos terminados: {terminados}")
        elif opcion == "3":
            break
        else:
            print("Opción no válida")
            