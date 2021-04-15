import ast
import asyncio
import inspect
import sqlite3
import time
import levels

import discord

import configuration
import util


# Custom exceptions we can raise
class CommandSyntaxError(Exception):
    pass


# --------------------------------------------------#
# SYSTEM COMMANDS #
# --------------------------------------------------#

'''async def _supersecretcommand(message, parameters):
    """adds role specific emotes"""
    with open("file.png", 'rb') as pic:
        arole=message.guild.get_role(int(parameters))
        await message.guild.create_custom_emoji(name='netherite', image=pic.read(), roles=[arole], reason="suggestion 371")

_supersecretcommand.command_data = {
    "syntax": "_a",
    "aliases": ["_aaaa"],
    "role_requirements": [configuration.MODERATOR_ROLE]
}'''

async def help(message, parameters):
    """Help command - Lists all commands, or gives info on a specific command."""

    if parameters is None:
        # Get a string listing all commands
        all_commands = "\n".join(
            [function.__name__ for function in command_list])
        # Make one of those fancy embed doohickies
        help_embed = discord.Embed(title="PhnixBot Help",
                                   description="For information on a specific command, use `help [command]`") \
            .add_field(name="Commands", value=all_commands)
        # Sent it
        await message.channel.send(embed=help_embed)

    else:
        # Try getting information on a specified command
        try:
            cmd = command_aliases_dict[parameters]
        except KeyError:
            await message.channel.send(
                f"Unknown command `{parameters}`.\nUse this command without any parameters for a list of valid commands.")
            return

        # Get info
        cmd_name = cmd.__name__

        cmd_syntax = "`" + cmd.command_data["syntax"] + "`"

        cmd_aliases_list = cmd.command_data["aliases"]
        cmd_aliases_str = "None" if len(cmd_aliases_list) == 0 else \
            "`" + "`, `".join(cmd_aliases_list) + "`"

        cmd_roles = cmd.command_data["role_requirements"]
        cmd_roles_str = ", ".join([f"<@&{role_id}>" for role_id in cmd_roles])

        # Will default to None if not present
        cmd_desc = cmd.command_data.get("description")

        # Build embed
        help_embed = discord.Embed(title=cmd_name, description=cmd_desc) \
            .add_field(name="Syntax", value=cmd_syntax) \
            .add_field(name="Aliases", value=cmd_aliases_str) \
            .add_field(name="Roles", value=cmd_roles_str)

        # Send
        await message.channel.send(embed=help_embed)

help.command_data = {
    "syntax": "help [command]",
    "aliases": ["?"],
    "role_requirements": [configuration.EVERYONE_ROLE]
}


# --------------------------------------------------#
# MISC COMMANDS #
# --------------------------------------------------#
async def test(message, parameters):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")

test.command_data = {
    "syntax": "test",
    "aliases": ["twoplustwo"],
    "role_requirements": [configuration.MODERATOR_ROLE]
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


async def replytome(message, parameters):
    if parameters == None:
        text = util.choose_random(("ok", "no"))
    else:
        text = parameters
    await message.channel.send(content=text, reference=message)

replytome.command_data = {
    "syntax": "replytome [text to echo]",
    "aliases": [],
    "role_requirements": [configuration.EVERYONE_ROLE]
}


async def aa(message, parameters):
    await message.channel.send(content="AAAAAAAAAAAAAAAAAAAAAAAA", reference=message)

aa.command_data = {
    "syntax": "AAAAAAAAAAAAAAAAAAAAAA",
    "aliases": ["a"*a for a in range(1, 12)],
    "role_requirements": [configuration.EVERYONE_ROLE],
    "description": "AAAAAAAAAAAAAAAAAA"
}


# --------------------------------------------------#
# MODERATION COMMANDS #
# --------------------------------------------------#

async def warn(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')
    sqlite_client = sqlite3.connect('bot_database.db')
    sqlite_client.execute('''INSERT INTO WARNS (ID, REASON, TIMESTAMP) \
        VALUES(:member_id, :reason, :time)''',
                          {'member_id': member_reason[0].id, 'reason': str(member_reason[1]),
                           'time': round(time.time())})
    sqlite_client.commit()
    sqlite_client.close()
    await message.channel.send(
        f"Warned {member_reason[0].name}#{member_reason[0].discriminator} for {member_reason[1]}")

warn.command_data = {
    "syntax": "warn <member> | [reason]",
    "aliases": [],
    "role_requirements": [configuration.MODERATOR_ROLE]
}


async def warns(message, parameters):
    member = await util.get_member_by_id_or_name(message, parameters)

    if member == None:
        raise CommandSyntaxError('You must specify a valid user.')

    sqlite_client = sqlite3.connect('bot_database.db')
    warn_list = sqlite_client.execute('''SELECT REASON, TIMESTAMP FROM WARNS WHERE ID = :member_id''',
                                      {'member_id': member.id}).fetchall()
    sqlite_client.close()

    if warn_list == []:
        await message.channel.send("User has no warns")
        return

    warn_text = ''
    timestamp_text = ''

    for warn in warn_list:
        warn_text += str(warn[0]) + '\n'
        timestamp_text += str(warn[1]) + '\n'

    warn_embed = discord.Embed(title="Warns", description=f"<@{member.id}>") \
        .add_field(name="Reason", value=warn_text) \
        .add_field(name="Timestamp", value=timestamp_text)

    await message.channel.send(embed=warn_embed)

warns.command_data = {
    "syntax": "warns <member>",
    "aliases": [],
    "role_requirements": [configuration.MODERATOR_ROLE]
}


async def mute(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)
    if member_reason == (None, None):
        raise CommandSyntaxError('You must specify a valid user/duration.')

    try:
        time_reason = member_reason[1].split(maxsplit=1)
        multiplier = configuration.TIME_MULIPLIER[time_reason[0][-1]]
        mute_time = int(time_reason[0][:-1]) * multiplier
    except:
        raise CommandSyntaxError('You must specify a valid duration.')

    roles = member_reason[0].roles
    try:
        await member_reason[0].add_roles(message.guild.get_role(configuration.MUTED_ROLE))
    except:
        await message.channel.send("I don't have perms to give mute role")
        return

    forbidden_role_flag = False

    for role in roles[1:]:
        try:
            await member_reason[0].remove_roles(role)
        except discord.errors.Forbidden:
            forbidden_role_flag = True

    if forbidden_role_flag:
        await message.channel.send("I don't have perms to give remove all their roles")

    await warn(message, f'{member_reason[0].id} MUTE - {member_reason[1]}')

    sqlite_client = sqlite3.connect('bot_database.db')
    try:
        sqlite_client.execute('''INSERT INTO MUTES (ID, TIMESTAMP, ROLES) \
            VALUES(:member_id, :timestamp, :roles) ''',
                              {'member_id': member_reason[0].id, 'timestamp': round(time.time()) + mute_time,
                               'roles': str([role.id for role in roles[1:]])})
    except sqlite3.IntegrityError:
        await message.channel.send('User is already muted')

    sqlite_client.commit()
    sqlite_client.close()
    await asyncio.sleep(mute_time)
    await unmute(message, str(member_reason[0].id))

mute.command_data = {
    "syntax": "mute <member> | <duration<s|m|h|d|y>> [reason]",
    "aliases": [],
    "role_requirements": [configuration.MODERATOR_ROLE]
}


async def unmute(message, parameters, guild=False, silenced=False):
    """
    Unmutes member
    Params:
    message: discord.message/guild object
    parameters: Parameters
    guild: if the message parameter is a guild object"""

    if guild:
        member = message.get_member(parameters)
    else:
        member = await util.get_member_by_id_or_name(message, parameters)

    if member == None:
        if not silenced:
            raise CommandSyntaxError('You must specify a valid user.')

    sqlite_client = sqlite3.connect('bot_database.db')
    roles = sqlite_client.execute('''SELECT ROLES FROM MUTES WHERE ID=:member_id''',
                                  {'member_id': member.id}).fetchone()
    sqlite_client.execute('''DELETE FROM MUTES WHERE ID=:member_id''',
                          {'member_id': member.id})
    sqlite_client.commit()
    sqlite_client.close()

    if roles == None and not guild:
        if not silenced:
            await message.channel.send('User is not muted')
        return

    roles = ast.literal_eval(roles[0])
    if guild:
        await member.remove_roles(message.get_role(configuration.MUTED_ROLE))
    else:
        await member.remove_roles(message.guild.get_role(configuration.MUTED_ROLE))
        
    try:
        for role in roles:
            if guild:
                message.get_role(role)
            else:
                role = message.guild.get_role(role)
            if role == None:
                continue

            await member.add_roles(role)
    except:
        pass

    if not silenced:
        await message.channel.send(f'Unmuted {member.name}#{member.discriminator} ({member.id})')

unmute.command_data = {
    "syntax": "unmute <member>",
    "aliases": [],
    "role_requirements": [configuration.MODERATOR_ROLE]
}


async def kick(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        # await message.guild.kick(member_reason[0], reason=member_reason[1])
        await message.channel.send(
            f"Kicked {member_reason[0].name}#{member_reason[0].discriminator} ({member_reason[0].id}) for {member_reason[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to kick")

kick.command_data = {
    "syntax": "kick <member> | [reason]",
    "aliases": ["kcik"],
    "role_requirements": [configuration.MODERATOR_ROLE]
}


async def ban(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await message.guild.ban(member_reason[0], reason=member_reason[1], delete_message_days=0)
        await message.channel.send(
            f"Banned {member_reason[0].name}#{member_reason[0].discriminator} ({member_reason[0].id}) for {member_reason[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to ban")

ban.command_data = {
    "syntax": "ban <member> | [reason]",
    "aliases": [],
    "role_requirements": [configuration.MODERATOR_ROLE]
}


# --------------------------------------------------#
# LEVEL COMMANDS #
# --------------------------------------------------#
async def rank(message, parameters):
    if not parameters == None:
        member = await util.get_member_by_id_or_name(message, parameters)
        if member == None:
            raise CommandSyntaxError('You must specify a valid user.')
    else:
        member = message.author

    sqlite_client = sqlite3.connect('bot_database.db')
    user_xp = sqlite_client.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                    {'user_id': member.id}).fetchone()
    if user_xp == None:
        await message.channel.send("The user isn't ranked yet.")
        return

    user_rank = sqlite_client.execute('''SELECT COUNT(*)+1 FROM LEVELS WHERE XP > :user_xp''',
                                      {'user_xp': user_xp[0]}).fetchone()

    rank_embed = discord.Embed(title="Rank", description=f"<@{member.id}>") \
        .add_field(name="Total XP:", value=user_xp[0]) \
        .add_field(name="Level:", value=user_xp[1]) \
        .add_field(name="Rank:", value="#" + str(user_rank[0])) \
        .add_field(name="XP until level up:", value=await levels.xp_needed_for_level(user_xp[1]) - user_xp[0])
        
    await message.channel.send(embed=rank_embed)

rank.command_data = {
    "syntax": "rank",
    "aliases": ["wank"],
    "role_requirements": [configuration.EVERYONE_ROLE]
}


command_list = []
command_aliases_dict = {}

_ = None  # Fix to stop vars() size from changing in for loop
for _ in vars():
    if inspect.iscoroutinefunction(vars()[_]):
        command_list.append(vars()[_])

for function in command_list:
    # Add the command's name itself as an alias
    command_aliases_dict[function.__name__] = function
    # Iterate through all aliases and add them as aliases
    for alias in function.command_data["aliases"]:
        command_aliases_dict[alias] = function
