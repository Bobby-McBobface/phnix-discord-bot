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
async def test(message, params, client):
    """A command named 'test'
    Parameters:
    message: discord.Message
    params: The text after the command name. Str or None
    client: discord.Client
    """
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.command_data = {
  "syntax": "test",
  "description": "Returns 2 + 2"
  "alias": ["twoplustwo"],
  "role_requirements": {configuration.MODERATOR_ROLE}
}
```
# How to run
- Make a folder called env
- Make a file in that folder called "token" and put your Discord Bot token there
- Make file called twitch_client_id and put your Twitch application's id there
- Make file called twitch_secret and put your Twitch application's secret there
- Run setup_data.py
- Run main.py
