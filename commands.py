import configuration
import data
import main
import util
import discord

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
    formatted_parameters = await util.split_into_member_and_reason(message, parameters)
    member = formatted_parameters[0]
    
    if member == None:
        await message.channel.send(f"Invalid syntax/user! Usage: {kick.command_data['syntax']}")
        return
    
    try:     
        # await message.guild.kick(member, reason=formatted_parameters[1])
        await message.channel.send(f"Kicked {member.name} for {formatted_parameters[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to kick")
                       
kick.command_data = {
  "syntax": "kick <member> | [reason]",
  "aliases": [],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

async def ban(message, parameters):  
    formatted_parameters = await util.split_into_member_and_reason(message, parameters)
    member = formatted_parameters[0]
    
    if member == None:
        await message.channel.send(f"Invalid syntax/user! Usage: {ban.command_data['syntax']}")
        return
    
    try:     
        await message.guild.ban(member, reason=formatted_parameters[1], delete_message_days=0)
        await message.channel.send(f"Banned {member.name} for {formatted_parameters[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to ban")        
                 
ban.command_data = {
  "syntax": "ban <member> | [reason]",
  "aliases": [],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

#--------------------------------------------------#
# LEVEL COMMANDS #
#--------------------------------------------------#
async def rank(message, parameters):
    try:
         # Horizontal scroll bar + PEP 8 is fuming right now
        await message.channel.send(f"XP count: {str(data.level_dict[message.author.id])} \nRank: {str(sorted(data.level_dict.items(), key=lambda x: x[1], reverse=True).index((message.author.id, data.level_dict[message.author.id]))+1)}")
    except KeyError:
        await message.channel.send("You aren't ranked yet! Send some messages first and try again later")
rank.command_data = {
  "syntax": "rank",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}
