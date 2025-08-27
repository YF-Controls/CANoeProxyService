from dataclasses import dataclass
from typing import Dict, Any

'''
  author: cyanezf YF-Controls
  date: 2024-01-15
  version: 1.0.0
  description: Service model for CanOeService
'''

@dataclass
class ServiceModel:
  """Service model class
  """
  name: str
  displayName: str
  description: str
  host: str
  port: int

  @classmethod
  def from_dic(cls, data: Dict[str, Any]) -> 'ServiceModel':
    """Create ServiceModel from dictionary
    """
    return cls(
      name = data['name'],
      displayName = data['displayName'],
      description = data['description'],
      host = data['host'],
      port = data['port']
    )