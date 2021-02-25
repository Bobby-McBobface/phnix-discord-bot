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
Dats structure
```py
  
level_dict = {
  # Format: User ID: XP amount
  # Also add the current level and amount to next level so we don't have recalculate each time
  # And sort by xp so we can easily count rank places
  # https://www.desmos.com/calculator/yjvvpuq1jn
}

warn_dict = {
  # Format: User ID: [Warning1, Warning2]
  # Warning object: <Reason for warn, Timestamp>
}

mute_dict = {
  # Format: User ID: {Timestamp: Unmute timestamp, Previous roles: [Previous role1, Previous role2]
}
```
