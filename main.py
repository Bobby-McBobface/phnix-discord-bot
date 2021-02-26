import discord
import inspect
import configuration
import commands
import levels
import data
import util

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
        
class PhnixBotClient(discord.Client):
    async def on_ready(self):
        """Runs when the bot is operational"""
        print('PhnixBot is ready')
        await levels.clear_chatted_loop()
        
    async def on_message(self, message):
        """Runs every time the bot notices a message being sent anywhere."""

        # Ignore bot accounts
        if message.author.bot == True: return
        
        #EXP/leveling system
        await levels.add_exp(message.author.id)
        
        # COMMANDS: Check if it has our command prefix, or starts with a mention of our bot
        command_text = await util.check_for_and_strip_prefixes(message.content, (configuration.PREFIX, self.user.mention, f"<@!{self.user.id}>"))
        # If there was a command prefix...
        if command_text is not None:
            
            # Split the command into 2 parts, command name and parameters
            split_command_text = command_text.split(maxsplit=1)
            try:
                command_name = split_command_text[0].lower()
            except IndexError:
                # No command specified
                return
            try:
                parameters = split_command_text[1]
            except IndexError:
                # No paramaters specified
                parameters = None
            
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
                     await command_function(message, parameters)
                     return # So we don't run it more than once

if __name__ == '__main__':

    with open('env/token') as file:
        token = file.read()

    client = PhnixBotClient()
    client.run(token)

    print('PhnixBot killed')
