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
@command({
  "syntax": "test",
  "description": "Returns 2 + 2"
  "alias": ["twoplustwo"],
  "role_requirements": {configuration.MODERATOR_ROLE}
})
async def test(message, params, client):
    """A command named 'test'
    Parameters:
    message: discord.Message
    params: The text after the command name. Str or None
    client: discord.Client
    """
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
```
