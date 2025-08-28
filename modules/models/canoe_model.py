from dataclasses import dataclass
from typing import List, Dict, Any
from .canoe_cfg_model import CanOeCfgModel

'''
  author: cyanezf YF-Controls
  date: 2024-01-15
  version: 1.0.0
  description: CanOe model class for CanOeService
'''

@dataclass
class CanOeModel:
  """CanOe Model class
  """
  path: str
  exe: str
  cfgs: list[CanOeCfgModel]

  @classmethod
  def from_dic(cls, data: Dict[str, Any]) -> 'CanOeModel':
    """Create CanOeModel from dictionary
    """
    cfgs = [CanOeCfgModel.from_dic(cfg) for cfg in data.get('cfgs', [])]
    return cls(
      path = data['path'],
      exe = data['exe'],
      cfgs = cfgs
    )
  
  def get_cfg_id_by_path(self, path: str) -> Dict[str, None]:
    """Get the ID of a CanOeCfgModel by its path.
    Args:
      path (str): The path of the configuration file to search for.
    Returns:
      str | None: The ID of the configuration if found, otherwise None.
    """
    for cfg in self.cfgs:
      if cfg.path.lower() == path.lower():
        return cfg.id
    return None
  
  def get_cfg_by_id(self, cfg_id: str) -> Dict['CanOeCfgModel', None]:
    '''Get the CanOeCfgModel by its ID.
    Args:
      cfg_id (str): The ID of the configuration to search for.
    Returns:
      CanOeCfgModel | None: The configuration model if found, otherwise None.
    '''
    
    for cfg in self.cfgs:
      if cfg.id == cfg_id:
        return cfg
    return None
  
  
