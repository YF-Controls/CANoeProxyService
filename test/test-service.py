# -*- coding: utf-8 -*-
# Script de servicio Windows válido (UTF-8)
# Service libraries
import win32serviceutil
import win32service
import win32event
import servicemanager
# Datetime libraries
from datetime import datetime
import time
# Communication libraries
import socket
import threading
# User modules
from CanOeService.modules.config_model.config_model import Config, CanOeConfig
import CanOeService.modules.process_util as app
from modules.can_oe_command import CanOeCommands
from modules.tcp_client import TCPClient
from CanOeService.modules.config_model.config_model import Config

from CanOeService.can_oe_service import TCPServer



if __name__ == '__main__':

  print('start')
  config = Config.from_json(r'c:\CanOeHandler\config.json')
  commands = CanOeCommands.from_json(r'c:\CanOeHandler\can_oe_command.json')
  server = TCPServer(config, commands)
  server.start()
  print('end')
  