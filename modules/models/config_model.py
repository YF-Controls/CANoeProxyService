from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json
from pathlib import Path

from .service_model import ServiceModel
from .canoe_model import CanOeModel
from .log_model import LogModel

'''
  author: cyanezf YF-Controls
  date: 2024-01-15
  version: 1.0.0
  description: Configuration model for CanOeService
'''

@dataclass
class ConfigModel:
  ''' Configuration model for CanOeService
  '''
  
  version: str
  description: str
  author: str
  service: ServiceModel
  canOe: CanOeModel
  log: LogModel
  
  @classmethod
  def from_dic(cls, data: Dict[str, Any]) -> 'ConfigModel':
    """Create ConfigModel from dictionary
    """
    
    return cls(
      version = data['version'],
      description = data['description'],
      author = data['author'],
      service = ServiceModel.from_dic(data['service']),
      canOe = CanOeModel.from_dic(data['canOe']),
      log = LogModel.from_dic(data['log'])
    )

  @classmethod
  def from_file(cls, file_path: str) -> 'ConfigModel':
    """Load ConfigModel from JSON file
    """
    if not Path(file_path).is_file():
      raise FileNotFoundError(f"Configuration file {file_path} not found.")
    
    with open(file_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
    
    return cls.from_dic(data)
  
  @classmethod
  def to_dict(cls, config: 'ConfigModel') -> Dict[str, Any]:
    """Convert ConfigModel to dictionary
    """
    return asdict(config)
  
  @classmethod
  def to_json(cls, config: 'ConfigModel', file_path: str) -> None:
    """Save ConfigModel to JSON file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
      json.dump(asdict(config), f, indent=2, ensure_ascii=False)
      
