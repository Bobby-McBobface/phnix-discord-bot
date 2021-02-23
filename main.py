import discord
import configuration
import commands

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
        
        #Format the command so it workes even if theres mIxEd cAsE
        commmand_text = command_text.lower()
        
        if command_text is not None:
            
            # TODO: add command logic here
            await message.channel.send(command_text)
        
