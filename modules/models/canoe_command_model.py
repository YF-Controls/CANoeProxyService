from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CanOeCommandModel:
  """CanOe Command model
  """
  id: str
  description: str
  parameter: list[str]
  responseOk: str
  responseNok: list[str]
  responseTimeout: float = 5.0
  
  @classmethod
  def from_dic(cls, data: Dict[str, Any]) -> 'CanOeCommandModel':
    """Create CanOeCommandModel from dictionary"""
    return cls(
      id = data['id'],
      description = data['description'],
      parameter = data['parameter'],
      responseOk = data['responseOk'],
      responseNok = data['responseNok'],
      responseTimeout = data.get('responseTimeout', 5.0)
    )