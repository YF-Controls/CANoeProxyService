import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import json
import sys
import os

class MyService(win32serviceutil.ServiceFramework):
  
    _svc_name_ = "TestCanOeService"
    _svc_display_name_ = "TEST CAN OE Service"
    _svc_description_ = "Servicio para procesamiento CAN OE"
    _svc_deps = []  # Dependencias opcionales

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
        
        socket.setdefaulttimeout(60)
        self.config_path = None
        self.config = {}

    def parse_arguments(self):
        """Parsear argumentos del servicio"""
        # Los argumentos vienen en sys.argv cuando se inicia el servicio
        args = sys.argv[1:]  # Excluir el nombre del script
        
        for i, arg in enumerate(args):
            if arg in ['-c', '--config', '/config'] and i + 1 < len(args):
                self.config_path = args[i + 1]
                break
            elif arg.startswith('config='):
                self.config_path = arg.split('=', 1)[1]
        
        # Valor por defecto si no se especifica
        if not self.config_path:
            self.config_path = r"C:\CanOeService\config.json"

    def load_config(self):
        """Cargar configuración desde archivo JSON"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                servicemanager.LogInfoMsg(f"Configuración cargada desde: {self.config_path}")
            else:
                servicemanager.LogWarningMsg(f"Archivo de configuración no encontrado: {self.config_path}")
                # Configuración por defecto
                self.config = {
                    "log_level": "INFO",
                    "interval": 5,
                    "database": {
                        "host": "localhost",
                        "port": 5432
                    }
                }
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error cargando configuración: {e}")
            self.config = {}

    def SvcStop(self):
        """Método llamado cuando se detiene el servicio"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogInfoMsg("Deteniendo servicio...")
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Método principal de ejecución del servicio"""
        # Registrar inicio del servicio
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        
        # Parsear argumentos y cargar configuración
        self.parse_arguments()
        self.load_config()
        
        servicemanager.LogInfoMsg(f"Servicio iniciado con configuración: {self.config_path}")
        self.main()

    def main(self):
        """Lógica principal del servicio"""
        try:
            # Ejemplo de uso de la configuración
            interval = self.config.get('interval', 5)
            log_level = self.config.get('log_level', 'INFO')
            
            servicemanager.LogInfoMsg(f"Iniciando con intervalo: {interval}s, nivel log: {log_level}")
            
            while True:
                # Verificar si se solicita detener el servicio
                if win32event.WaitForSingleObject(self.hWaitStop, interval * 1000) == win32event.WAIT_OBJECT_0:
                    servicemanager.LogInfoMsg("Servicio detenido por solicitud")
                    break
                
                # Tu lógica de procesamiento aquí
                self.process_data()
                
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error en el servicio: {e}")

    def process_data(self):
        """Método de ejemplo para procesamiento de datos"""
        # Aquí va tu lógica de negocio
        servicemanager.LogInfoMsg("Procesando datos CAN OE...")
        # time.sleep(1)  # Simular trabajo

if __name__ == '__main__':
    # Manejar línea de comandos para instalación/desinstalación
    if len(sys.argv) == 1:
        # Si no hay argumentos, mostrar ayuda
        print("Uso: python servicio.py [install|start|stop|remove] [--config path]")
        print("Ejemplo para instalar con configuración personalizada:")
        print('python servicio.py install --config "C:\\ruta\\personalizada\\config.json"')
    else:
        win32serviceutil.HandleCommandLine(MyService)