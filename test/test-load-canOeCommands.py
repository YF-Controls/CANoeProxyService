from modules.can_oe_command import CanOeCommands


commands = CanOeCommands.from_json(r'c:\CanOeHandler\can_oe_command.json')

cmd_id = commands.command_matches('Set_target DMFL_MMA ')

timeout = commands.get_response_timeout(cmd_id)

response = commands.response_matches('Authenticate Error data')

print(response)
print(len(response))
print(response[0])