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
async def test(message):
    """A command named 'test'"""
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
  # https://www.desmos.com/calculator/yjvvpuq1jn
}

warn_dict = {
  # Format: User ID: [Warning1, Warning2]
  # Warning object: <Reason for warn, Timestamp>
}

mute_dict = {
  # Format: User ID: {Timestamp: Unmute timestamp, Previous roles: [Previous role1, Previous role2]
}```
