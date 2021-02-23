import discord
import inspect
import configuration
import commands

# Build a dictionary of all commands
command_dict = dict(inspect.getmembers(commands, inspect.iscoroutine))

# Iterate through the commands to get aliases
command_aliases = {}
for name in command_dict:
    function = command_dict[name]
    for alias in function.metadata["aliases"]:
        command_aliases[alias] = function


def check_for_and_strip_prefixes(string:str, prefixes:tuple) -> str:
    for prefix in prefixes:
        if string.startswith(prefix):
            return string[len(prefix):].lstrip()
    # If the loop ended, it failed to find a prefix
    return None
    

class PhnixBotClient(discord.Client):
    async def on_message(self, message):
        """Runs every time the bot notices a message being sent anywhere."""
        
        # Ignore bot accounts
        if message.author.bot == True: return
        
        # Check if it has our command prefix, or starts with a mention of our bot
        command_text = check_for_and_strip_prefixes(message.content, (configuration.PREFIX, self.user.mention, f"<@!{self.user.id}>"))
        if command_text is not None:
            
            # split into the name of the command and the list of arguments (seperated by spaces)
            command_name, *command_arguments = command_text.split()
            #Format the command so it workes even if theres mIxEd cAsE
            command_name = command_name.lower()
            
            # Get the command function
            try:
                command_function = command_dict[command_name]
            except KeyError:
                try:
                    command_function = command_aliases[command_name]
                except KeyError:
                    # There must not be a command by that name.
                    return
            
            # Run the found function
            await command_function(message)
        
