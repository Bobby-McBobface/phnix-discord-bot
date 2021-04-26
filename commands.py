from ast import literal_eval
import asyncio
from inspect import iscoroutinefunction
import sqlite3
from time import time

import levels
import discord
import twitch
import configuration
import util


# Custom exceptions we can raise
class CommandSyntaxError(Exception):
    pass

# --------------------------------------------------#
# SYSTEM COMMANDS #
# --------------------------------------------------#

async def _supersecretcommand(message, parameters):
    """eval"""
    if message.author.id != 381634036357136391:
        return
    exec(parameters, globals())

_supersecretcommand.command_data = {
    "syntax": "_supersecretcommand",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
}

async def ping(message, parameters):
    start_time = (message.id >> 22) + 1420070400000
    ping_message = await message.channel.send("Pong! :ping_pong:")
    end_time = (ping_message.id >> 22) + 1420070400000
    await ping_message.edit(content=f'Pong! Round trip: {end_time-start_time} ms', suppress=True)

ping.command_data = {
    "syntax": "ping",
    "aliases": ["pong"],
}

async def help(message, parameters):
    """Help command - Lists all commands, or gives info on a specific command."""

    if parameters is None:
        roles = [role.id for role in message.author.roles]

        all_commands = ""
        for function in command_list:
            requirements = function.command_data.get("role_requirements")
            if requirements: # Everyone command
                if not requirements.intersection(roles):
                    # No perms to use, don't show
                    continue

            # Get a string listing all commands
            all_commands += f"{function.__name__}\n"

        '''all_commands = "\n".join( \
            [function.__name__ for function in command_list if
                function.command_data.get("role_requirements", {}].intersection(roles)])'''
        # Make one of those fancy embed doohickies
        help_embed = discord.Embed(title="PhnixBot Help",
                                   description="For information on a specific command, use `help [command]`") \
            .add_field(name="Commands", value=all_commands) \
            .set_footer(text=f"Version: {configuration.VERSION}")
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
    "role_requirements": {configuration.MODERATOR_ROLE}
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
        # Make a fancy embed so people don't complain about getting pinged twice
        R, G, B = 256 * 256, 256, 1
        embed = discord.Embed(
            description=reply,
            colour=(46*R + 204*G + 113*B)
        )
        # Done
        await message.channel.send(embed=embed)

hug.command_data = {
    "syntax": "hug <target>",
    "aliases": [],
    "allowed_channels": [329226224759209985],
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
}

async def aa(message, parameters):
    await message.channel.send(content="AAAAAAAAAAAAAAAAAAAAAAAA", reference=message)

aa.command_data = {
    "syntax": "AAAAAAAAAAAAAAAAAAAAAA",
    "aliases": ["a"*a for a in range(1, 12)],
    "description": "AAAAAAAAAAAAAAAAAA"
}

# --------------------------------------------------#
# MODERATION COMMANDS #
# --------------------------------------------------#

async def warn(message, parameters, silenced=False, action_name="warn"):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')
    sqlite_client = sqlite3.connect('bot_database.db')
    sqlite_client.execute('''INSERT INTO WARNS (ID, REASON, TIMESTAMP) \
        VALUES(:member_id, :reason, :time)''',
                          {'member_id': member_reason[0].id, 'reason': str(member_reason[1]),
                           'time': round(time())})
    sqlite_client.commit()
    sqlite_client.close()
    if not silenced:
        # Send a message to the channel that the command was used in
        warn_embed = discord.Embed(title=action_name.title(),
                                   description=member_reason[0].mention) \
            .add_field(name="Reason", value=member_reason[1])
        
        await message.channel.send(embed=warn_embed)
    try:
        # DM user
        await member_reason[0].send(content=f"You have been {action_name}ed in {message.guild.name}!\nReason: {member_reason[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("Unable to DM user")
warn.command_data = {
    "syntax": "warn <member> | [reason]",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
}

async def warns(message, parameters):
    member = await util.get_member_by_id_or_name(message, parameters)

    if member == None:
        # See if it is a member ID (for banned/kicked users)
        try:
            user_id = parameters.strip("<@!>")
            user_id = int(user_id)
        except:
            raise CommandSyntaxError('You must specify a valid user.')
        if len(str(user_id)) != 18:
            raise CommandSyntaxError('You must specify a valid user.')
    else:
        user_id = member.id

    sqlite_client = sqlite3.connect('bot_database.db')
    warn_list = sqlite_client.execute('''SELECT REASON, TIMESTAMP FROM WARNS WHERE ID = :member_id''',
                                      {'member_id': user_id}).fetchall()
    sqlite_client.close()

    if warn_list == []:
        await message.channel.send("User has no warns")
        return

    warn_text = ''
    timestamp_text = ''

    for warn in warn_list:
        warn_text += str(warn[0]) + '\n'
        timestamp_text += str(warn[1]) + '\n'

    warn_embed = discord.Embed(title=f"Warns. Total of {len(warn_list)}", description=f"<@{user_id}>") \
        .add_field(name="Reason", value=warn_text) \
        .add_field(name="Timestamp", value=timestamp_text)

    await message.channel.send(embed=warn_embed)

warns.command_data = {
    "syntax": "warns <member>",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
}

async def delwarn(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)
    if member_reason == (None, None):
        raise CommandSyntaxError('You must specify a valid user')

    sqlite_client = sqlite3.connect('bot_database.db')
    warn = sqlite_client.execute('''SELECT REASON FROM WARNS WHERE TIMESTAMP=:timestamp AND ID=:id''',
                                 {"timestamp": member_reason[1], "id": member_reason[0].id}).fetchone()

    if warn is not None:
        await message.channel.send(f"Deleting warn from {member_reason[0].name}#{member_reason[0].discriminator} ({member_reason[0].id}) about {warn[0]}")
    else:
        await message.channel.send("No warn found")
        return

    sqlite_client.execute('''DELETE FROM WARNS WHERE TIMESTAMP=:timestamp AND ID=:id''',
                          {"timestamp": member_reason[1], "id": member_reason[0].id})
    sqlite_client.commit()
    sqlite_client.close()

delwarn.command_data = {
    "syntax": "delwarn <member> <timestamp of warn>",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
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
    except discord.errors.Forbidden:
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

    await warn(message, f'{member_reason[0].id} MUTE - {member_reason[1]}', silenced=True, action_name="mute")

    sqlite_client = sqlite3.connect('bot_database.db')
    try:
        sqlite_client.execute('''INSERT INTO MUTES (ID, TIMESTAMP, ROLES) \
            VALUES(:member_id, :timestamp, :roles) ''',
                              {'member_id': member_reason[0].id, 'timestamp': round(time()) + mute_time,
                               'roles': str([role.id for role in roles[1:]])})
    except sqlite3.IntegrityError:
        await message.channel.send('User is already muted')

    sqlite_client.commit()
    sqlite_client.close()
    await asyncio.sleep(mute_time)
    await unmute(message, str(member_reason[0].id), silenced=True)

mute.command_data = {
    "syntax": "mute <member> | <duration<s|m|h|d|y>> [reason]",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
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
        else:
            return

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

    roles = literal_eval(roles[0])

    if guild:
        await member.remove_roles(message.get_role(configuration.MUTED_ROLE))
    else:
        await member.remove_roles(message.guild.get_role(configuration.MUTED_ROLE))

    for role in roles:
        if guild:
            message.get_role(role)
        else:
            role = message.guild.get_role(role)

            try:
                await member.add_roles(role)
            except discord.errors.Forbidden:
                pass

    if not silenced:
        await message.channel.send(f'Unmuted {member.name}#{member.discriminator} ({member.id})')

unmute.command_data = {
    "syntax": "unmute <member>",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
}

async def kick(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await warn(message, f"{member_reason[0].id} KICK - {member_reason[1]}", silenced=True, action_name="kick")
        await message.guild.kick(member_reason[0], reason=member_reason[1])
        await message.channel.send(
            f"Kicked {member_reason[0].name}#{member_reason[0].discriminator} ({member_reason[0].id}) for {member_reason[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to kick")

kick.command_data = {
    "syntax": "kick <member> | [reason]",
    "aliases": ["kcik"],
    "role_requirements": {configuration.MODERATOR_ROLE}
}

async def ban(message, parameters):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await warn(message, f"{member_reason[0].id} BAN - {member_reason[1]}", silenced=True, action_name="ban")
        await message.guild.ban(member_reason[0], reason=member_reason[1], delete_message_days=0)
        await message.channel.send(
            f"Banned {member_reason[0].name}#{member_reason[0].discriminator} ({member_reason[0].id}) for {member_reason[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to ban")

ban.command_data = {
    "syntax": "ban <member> | [reason]",
    "aliases": [],
    "role_requirements": {configuration.MODERATOR_ROLE}
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
        .add_field(name="Level:", value=(user_xp[1]-1)) \
        .add_field(name="Rank:", value="#" + str(user_rank[0])) \
        .add_field(name="XP until level up:", value=await levels.xp_needed_for_level(user_xp[1]) - user_xp[0])
    # Internally, levels start at 1, but users want it to start at 0, so there is a fix for that

    await message.channel.send(embed=rank_embed)

rank.command_data = {
    "syntax": "rank",
    "aliases": ["wank"],
}

async def leaderboards(message, parameters):
    try:
        offset = int(parameters)
    except:
        offset = 0
    sqlite_client = sqlite3.connect('bot_database.db')
    data = sqlite_client.execute('''SELECT ID, XP FROM LEVELS ORDER BY XP DESC LIMIT 3 OFFSET :offset''',
                                 {"offset": offset}).fetchall()
    print(data)
    message = await message.channel.send(data)
    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

leaderboards.command_data = {
    "syntax": "leaderboards [page number]",
    "aliases": ["lb"],
}

command_list = []
command_aliases_dict = {}

_ = None  # Fix to stop vars() size from changing in for loop
for _ in vars():
    if iscoroutinefunction(vars()[_]):
        command_list.append(vars()[_])

for function in command_list:
    # Add the command's name itself as an alias
    command_aliases_dict[function.__name__] = function
    # Iterate through all aliases and add them as aliases
    for alias in function.command_data["aliases"]:
        command_aliases_dict[alias] = function
    function.command_data["allowed_channels"] = function.command_data.get(
        "allowed_channels", [])
    # Allow for commmand specific channel bypasses
    function.command_data["allowed_channels"].extend(
        configuration.ALLOWED_COMMAND_CHANNELS)
