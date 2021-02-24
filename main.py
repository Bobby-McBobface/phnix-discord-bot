import discord
import inspect
import configuration
import commands
import levels

# Build a dictionary of all commands
command_dict = dict(inspect.getmembers(commands, inspect.isfunction))

command_aliases_dict = {}
# Iterate through the commands to get aliases
for name in command_dict:
    # Get the value that we're setting them to from the other dict
    function = command_dict[name]
    # Add the command's name itself as an alias
    command_aliases_dict[name] = function
    # Iterate through all aliases and add them as aliases
    for alias in function.command_data["aliases"]:
        command_aliases_dict[alias] = function

def check_for_and_strip_prefixes(string:str, prefixes:tuple) -> str:
    """If `string` starts with one of the given prefixes, return the string sans the prefix. Otherwise, returns None."""
    for prefix in prefixes:
        if string.startswith(prefix):
            return string[len(prefix):].lstrip()
    # If the loop ended, it failed to find a prefix
    return None
    

class PhnixBotClient(discord.Client):
    async def on_ready(self):
        """Runs when the bot is operational"""
        print('PhnixBot is ready')
        await levels.clear_chatted_loop()
        
    async def on_message(self, message):
        """Runs every time the bot notices a message being sent anywhere."""
        print(message.content)
        # Ignore bot accounts
        if message.author.bot == True: return
        
        #TODO: EXP/leveling system here?
        await levels.add_exp(message.author.id)
        
        # COMMANDS: Check if it has our command prefix, or starts with a mention of our bot
        command_text = check_for_and_strip_prefixes(message.content, (configuration.PREFIX, self.user.mention, f"<@!{self.user.id}>"))
        # If there was a command prefix...
        if command_text is not None:
            
            # Split into the name of the command and the list of arguments (seperated by spaces)
            command_name = command_text.split(maxsplit=1)[0]
            # Format the command so it workes even if theres mIxEd cAsE
            command_name = command_name.lower()

            # Get the command function
            try:
                command_function = command_aliases_dict[command_name]
            except KeyError:
                # There must not be a command by that name.
                return
            
            # Do role checks
            for role in message.author.roles:
                if role.id in command_function.command_data['role_requirements']:
                     # Run the found function
                     await command_function(message)
                     return # So we don't run it more than once
                
with open('env/token') as file:
    token = file.read()

client = PhnixBotClient()
client.run(token)

print('hello')
