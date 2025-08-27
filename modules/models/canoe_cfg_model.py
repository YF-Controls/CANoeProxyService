from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .canoe_command_model import CanOeCommandModel

'''
  author: cyanezf YF-Controls
  date: 2024-01-15
  version: 1.0.0
  description: Configuration model for CanOeService
'''

@dataclass
class CanOeCfgModel:
  """CanOe Config model
  """
  id: str
  description: str
  path: str
  host: str
  port: int
  #commands: list[CanOeCommandModel]

  @classmethod
  def from_dic(cls, data: Dict[str, Any]) -> 'CanOeCfgModel':
    """Create CanOeCfgModel from dictionary
    """
    #commands = [CanOeCommandModel.from_dic(cmd) for cmd in data.get('commands', [])]
    return cls(
      id = data['id'],
      description = data.get('description', 'No description provided'),
      path = data['path'],
      host = data['host'],
      port = data['port'],
      #commands = commands
    )

