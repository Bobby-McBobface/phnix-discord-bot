import configuration
import data
import main
import util
import discord

# Custom exceptions we can raise
class CommandSyntaxError(Exception): pass


#--------------------------------------------------#
# SYSTEM COMMANDS #
#--------------------------------------------------#

async def help(message, parameters):
    """Help command - Lists all commands, or gives info on a specific command."""
    
    if parameters is None: # No specific command requested - List every command
        # Get a string listing all commands
        all_commands = "\n".join(main.command_dict)
        # Make one of those fancy embed doohickies
        help_embed = discord.Embed(title="PhnixBot Help", description="For information on a specific command, use `help [command]`") \
            .add_field(name="Commands", value=all_commands)
        # Sent it
        await message.channel.send(embed=help_embed)
        
    else: # There was a paramater - Get help on a specific command
        await message.channel.send("[TODO]")
help.command_data = {
  "syntax": "help [command]",
  "aliases": ["?"],
  "role_requirements": [configuration.EVERYONE_ROLE]
}

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
        raise CommandSyntaxError
    else:
        await message.channel.send(" ".join(parameters))
pad.command_data = {
  "syntax": "pad <message>",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}

async def hug(message, parameters):
    # Make sure someone was specified
    if parameters == None:
        raise CommandSyntaxError("You must specify someone to hug.")
    else:
        # Get users
        hugger = message.author.mention
        target = parameters
        # Get a random message and fill it in
        choice = util.choose_random(configuration.STRINGS_HUG)
        reply = choice.format(hugger=hugger, target=target)
        # Done
        await message.channel.send(reply)
hug.command_data = {
  "syntax": "hug <target>",
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
        raise CommandSyntaxError('You must specify a valid user.')
        
    try:     
        # await message.guild.kick(member, reason=formatted_parameters[1])
        await message.channel.send(f"Kicked {member.name}#{member.discriminator} for {formatted_parameters[1]}")
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
        raise CommandSyntaxError('You must specify a valid user.')
        
    try:     
        await message.guild.ban(member, reason=formatted_parameters[1], delete_message_days=0)
        await message.channel.send(f"Banned {member.name}#{member.discriminator} for {formatted_parameters[1]}")
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
    if not parameters == None:
        member = await util.get_member_by_id_or_name(message, parameters)
        if member == None:
            raise CommandSyntaxError('You must specify a valid user.')
    else:
        member = message.author
    try:
         # Horizontal scroll bar + PEP 8 is fuming right now
        await message.channel.send(f"XP count: {str(data.level_dict[member.id])} \nRank: {str(sorted(data.level_dict.items(), key=lambda x: x[1], reverse=True).index((member.id, data.level_dict[member.id]))+1)}")
    except KeyError:
        await message.channel.send("The user isn't ranked yet!")
rank.command_data = {
  "syntax": "rank",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}
