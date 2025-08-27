import os
import sys
import json
from modules.models.config_model import ConfigModel

def test_config_loading():
  """Test para verificar la carga de configuración"""
  print("\nTEST #######################################################################")
  
  # Ruta al archivo config.json (ajusta según tu estructura)
  config_path = os.path.join(os.path.dirname(__file__), 'config.json')
  print("path:", config_path)
        
  try:
    # Cargar configuración
    config = ConfigModel.from_file(config_path)
    
    print("✅ Configuración cargada exitosamente")
    print(f"📋 Versión: {config.version}")
    print(f"🖥️  Servicio: {config.service.name}")
    print(f"🔌 Puerto: {config.service.port}")
    print(f"📊 Configuraciones CANoe: {len(config.canOe.cfgs)}")
    
    # Mostrar información de los commands
    for i, cfg in enumerate(config.canOe.cfgs):
      print(f"\n🔧 Config {i+1}: {cfg.id}")
      print(f"   Descripción: {cfg.description}")
      print(f"   Commands: {len(cfg.commands)}")
      
      for cmd in cfg.commands:
        print(f"     - {cmd.id}: {cmd.description}")
  
    return True
    
  except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo {config_path}")
    return False
  except json.JSONDecodeError as e:
    print(f"❌ Error en formato JSON: {e}")
    return False
  except Exception as e:
    print(f"❌ Error inesperado: {e}")
    return False


if __name__ == "__main__":
  test_config_loading()