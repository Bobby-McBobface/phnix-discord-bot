import configuration
import data
import main
import util

#--------------------------------------------------#
# MISC COMMANDS #
#--------------------------------------------------#
async def test(message, parameters):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.command_data = {
  "syntax": "test",
  "aliases": ["twoplustwo"],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

async def pad(message, parameters):
    """Spaces out your text"""
    if parameters == None:
        await message.channel.send("Usage: `pad <message>`")
    else:
        await message.channel.send(" ".join(parameters))
pad.command_data = {
  "syntax": "pad <message>",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
} 

#--------------------------------------------------#
# MODERATION COMMANDS #
#--------------------------------------------------#
'''async def warn(message, parameters):
    pass
pad.command_data = {
  "syntax": "pad <message>",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}

async def mute(message, parameters):
    pass
pad.command_data = {
  "syntax": "pad <message>",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}
'''
async def kick(message, parameters):  
    formatted_parameters = await util.split_into_member_and_reason(parameters)
    
    if formatted_parameters[0] = None:
        await message.channel.send("Invalid syntax/user! Usage:", kick.syntax)
        
    try:     
        await message.guild.kick(formatted_parameters[0], formatted_parameters[1])
    except discord.Forbidden:
        await message.channel.send("I don't have perms to kick")
                       
kick.command_data = {
  "syntax": "kick <member> [reason]",
  "aliases": [],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

async def ban(message, parameters):  
    formatted_parameters = await util.split_into_member_and_reason(parameters)
    
    if formatted_parameters[0] = None:
        await message.channel.send("Invalid syntax/user! Usage:", ban.syntax)
        
    try:     
        await message.guild.ban(formatted_parameters[0], formatted_parameters[1])
    except discord.Forbidden:
        await message.channel.send("I don't have perms to ban")        
                 
ban.command_data = {
  "syntax": "ban <member> [reason]",
  "aliases": [],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

#--------------------------------------------------#
# LEVEL COMMANDS #
#--------------------------------------------------#
async def rank(message, parameters):
    try:
        await message.channel.send(data.level_dict[message.author.id])
    except KeyError:
        await message.channel.send("You aren't ranked yet! Send some messages first and try again later")
rank.command_data = {
  "syntax": "rank",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}
