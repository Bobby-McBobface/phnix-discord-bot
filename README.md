# phnix-discord-bot

A command needs: \n
• function (aka the code)\n
• name used to invoke it\n
• roles required to use it\n
• aliases\n
• syntax & description (if we want a good help command)\n

Command example:

```py
async def my_command():
  return
my_command.name = 'command'
my_command.role_requirements = [roleID, roleID2] 
my_command.alias = [alias, alias2]
my_command.description = 'Does nothing'
```
