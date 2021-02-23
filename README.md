# phnix-discord-bot

A command needs:
• function (aka the code)
• name used to invoke it
• roles required to use it
• aliases
• syntax & description (if we want a good help command)

Command example:

```py
async def my_command():
  return
my_command.name = 'command'
my_command.role_requirements = [roleID, roleID2] 
my_command.alias = [alias, alias2]
my_command.description = 'Does nothing'
```
