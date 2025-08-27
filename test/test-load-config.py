from CanOeService.modules.config_model.config_model import Config

config = Config.from_json(r'c:\CanOeHandler\config.json')

print(config)
