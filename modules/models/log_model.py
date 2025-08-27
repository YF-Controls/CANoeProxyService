from dataclasses import dataclass
from typing import Dict, Any


'''
  author: cyanezf YF-Controls
  date: 2024-01-15
  version: 1.0.0
  description: Log model class for CanOeService
'''

@dataclass
class LogModel:
  """Log model class
  """
  help: str = "Log levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL"
  level: str = "DEBUG"
  printToConsole: bool = False
  filePath: str
  maxSize: int = 10485760  # 10 MB
  maxFiles: int = 20
  format: str = "%(asctime)s [%(levelname)-8s] %(message)-80s [%(name)s , %(funcName)s , %(lineno)d]"

  @classmethod
  def from_dic(cls, data: Dict[str, Any]) -> 'LogModel':
    """Create LogModel from dictionary
    """
    return cls(
      help = data.get('help', "Log levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL"),
      level = data.get('level', "DEBUG"),
      printToConsole = data.get('printToConsole', False),
      printToEventViewer = data.get('printToEventViewer', False),
      filePath = data.get('filePath', f"c:\CanOeProxy.log"),
      maxSize = data.get('maxSize', 10485760),
      maxFiles = data.get('maxFiles', 20),
      format = data.get('format', "%(asctime)s [%(levelname)-8s] %(message)-80s [%(name)s , %(funcName)s , %(lineno)d]")
    )
    
    