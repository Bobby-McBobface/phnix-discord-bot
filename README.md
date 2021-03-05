# phnix-discord-bot
```
A command needs: 
• function (aka the code)
• name used to invoke it
• roles required to use it
• aliases
• syntax & description (if we want a good help command)
````
Command example:

```py
async def test(message, params):
    """A command named 'test'
    Parameters:
    message: The discord.py message object
    params: The text after the command name. Str or None
    """
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.command_data = {
  "syntax": "test",
  "alias": ["twoplustwo"],
  "role_requirements": [configuration.MODERATOR_ROLE]
}
```
