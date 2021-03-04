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
    
    if isinstance(parameters, str):
        # Assume this means they requested an invalid command
        await message.channel.send(f"Unknown command `{parameters}`.\nUse this command without any parameters for a list of valid commands.")
    
    elif isinstance(parameters, dict):
        # Assume that the dict we've been given is the dictionary of all commands {name: function}
        # Therefore, send a list of every command...
        command_dict = parameters
        # Get a string listing all commands
        all_commands = "\n".join(command_dict)
        # Make one of those fancy embed doohickies
        help_embed = discord.Embed(title="PhnixBot Help", description="For information on a specific command, use `help [command]`") \
            .add_field(name="Commands", value=all_commands)
        # Sent it
        await message.channel.send(embed=help_embed)
        
    else:
        # Assume that parameters is a function that the user wants information on
        cmd = parameters
        # Get info
        cmd_name = cmd.__name__
        cmd_syntax = cmd.command_data["syntax"]
        cmd_aliases_list = cmd.command_data["aliases"]
        cmd_aliases_str = "None" if len(cmd_aliases_list) == 0 else \
            "`, `".join(cmd_aliases_list)
        cmd_roles = cmd.command_data["role_requirements"]
        # Build embed
        help_embed = discord.Embed(title=cmd_name) \
            .add_field(name="Syntax", value=f"`{cmd_syntax}`") \
            .add_field(name="Aliases", value=f"`{cmd_aliases_str}`") \
            .add_field(name="Roles", value=f"`{cmd_roles}`")
        # Send
        await message.channel.send(embed=help_embed)
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

    sqlite_client = sqlite3.connect('bot_database.db')
    user_xp = sqlite_client.execute('''SELECT XP FROM LEVELS WHERE ID=:user_id''',
                                    {'user_id': member.id}).fetchone()
    if user_xp == None:
        await message.channel.send("The user isn't ranked yet.")
        return
    
    user_list = sqlite_client.execute('''SELECT ID FROM LEVELS ORDER BY XP''')
    rank = 0
    for user in user_list:
        if user != member.id:
            rank += 1
        else:
            break
    await message.channel.send(f'XP: {user_xp[0]} \nRank: {rank}') 
                
rank.command_data = {
  "syntax": "rank",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}
