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
from enum import Enum


# Custom exceptions we can raise
class CommandSyntaxError(Exception):
    pass

class Category(Enum):
    MODERATION = {
        'friendly_name': 'Moderation', 
        'priority': 10
    }
    LEVELING = {
        'friendly_name': 'Leveling', 
        'priority': 1
    }
    DEVELOPMENT = {
        'friendly_name': 'Bot Development', 
        'priority': 100
    }
    SYSTEM = {
        'friendly_name': 'System commands', 
        'priority': 50
    }
    OTHER = {
        'friendly_name': 'Other', 
        'priority': -1
    }

# --------------------------------------------------#
# SYSTEM COMMANDS #
# --------------------------------------------------#

async def _supersecretcommand(message, parameters, client):
    """eval"""
    if message.author.id != 381634036357136391:
        return
    exec(parameters, globals())

_supersecretcommand.command_data = {
    "syntax": "_supersecretcommand",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.DEVELOPMENT
}

async def ping(message, parameters, client):
    start_time = (message.id >> 22) + 1420070400000
    ping_message = await message.channel.send("Pong! :ping_pong:")
    end_time = (ping_message.id >> 22) + 1420070400000
    await ping_message.edit(content=f'Pong! Round trip: {end_time-start_time} ms', suppress=True)

ping.command_data = {
    "syntax": "ping",
    "aliases": ["pong"],
    "category": Category.SYSTEM
}

async def help(message, parameters, client):
    """Help command - Lists all commands, or gives info on a specific command."""

    if parameters is None:
        roles = [role.id for role in message.author.roles]

        category_commands = ""
        last_category = None

         # Make one of those fancy embed doohickies
        help_embed = discord.Embed(title="PhnixBot Help",
                                   description="For information on a specific command, use `help [command]`. \n\
                                   Now [open source!](https://github.com/Bobby-McBobface/phnix-discord-bot)") \
                                   .set_footer(text=f"Version: {configuration.VERSION}")
        for function in command_list:
            requirements = function.command_data.get("role_requirements")
            if requirements: # Not @everyone command
                if not requirements.intersection(roles):
                    # No perms to use, don't show
                    continue

            if not last_category:
                # First command
                last_category = function.command_data["category"]

            elif function.command_data["category"] != last_category:
                # New category
                help_embed.add_field(name=last_category.value["friendly_name"], value=category_commands, inline=False)
                last_category = function.command_data["category"]
                category_commands = ''

            category_commands += f"{function.__name__}\n"

        # Add the last category
        help_embed.add_field(name=last_category.value["friendly_name"], value=category_commands, inline=False)

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

        cmd_roles = cmd.command_data.get("role_requirements", [configuration.EVERYONE_ROLE])
        # If no requirements, assumme it's for everyone
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
    "category": Category.SYSTEM
}

# --------------------------------------------------#
# MISC COMMANDS #
# --------------------------------------------------#
async def test(message, parameters, client):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")

test.command_data = {
    "syntax": "test",
    "aliases": ["twoplustwo"],
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.OTHER
}

async def pad(message, parameters, client):
    """Spaces out your text"""
    if parameters == None:
        raise CommandSyntaxError
    else:
        await message.channel.send(" ".join(parameters))

pad.command_data = {
    "syntax": "pad <message>",
    "category": Category.OTHER
}

async def hug(message, parameters, client):
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
    "allowed_channels": [329226224759209985, 827880703844286475],
    "category": Category.OTHER
}


async def replytome(message, parameters, client):
    if parameters == None:
        text = util.choose_random(("ok", "no"))
    else:
        text = parameters
    await message.channel.send(content=text, reference=message)

replytome.command_data = {
    "syntax": "replytome [text to echo]",
    "category": Category.OTHER
}

async def aa(message, parameters, client):
    await message.channel.send(content="AAAAAAAAAAAAAAAAAAAAAAAA", reference=message)

aa.command_data = {
    "syntax": "AAAAAAAAAAAAAAAAAAAAAA",
    "aliases": ["a"*a for a in range(1, 12)],
    "description": "AAAAAAAAAAAAAAAAAA",
    "category": Category.OTHER
}

# --------------------------------------------------#
# MODERATION COMMANDS #
# --------------------------------------------------#

async def warn(message, parameters, client, action_name="warned"):
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
    # Send a message to the channel that the command was used in
    warn_embed = discord.Embed(title=action_name.title(),
                                description=member_reason[0].mention) \
        .add_field(name="Reason", value=member_reason[1])
        
    await message.channel.send(embed=warn_embed)
    try:
        # DM user
        await member_reason[0].send(content=f"You have been {action_name} in {message.guild.name}!\nReason: {member_reason[1]}")
    except discord.errors.Forbidden:
        await message.channel.send("Unable to DM user")
warn.command_data = {
    "syntax": "warn <member> | [reason]",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

async def warns(message, parameters, client):
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
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

async def mywarns(message, parameters, client):
    await warns(message, str(message.author.id), client)

mywarns.command_data = {
    "syntax": "mywarns", 
    "description": "See your own warns",
    "category": Category.MODERATION
}

async def delwarn(message, parameters, client):
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
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

async def mute(message, parameters, client):
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

    sqlite_client = sqlite3.connect('bot_database.db')
    try:
        sqlite_client.execute('''INSERT INTO MUTES (ID, TIMESTAMP, ROLES) \
            VALUES(:member_id, :timestamp, :roles) ''',
                              {'member_id': member_reason[0].id, 'timestamp': round(time()) + mute_time,
                               'roles': str([role.id for role in roles[1:]])})
    except sqlite3.IntegrityError:
        await message.channel.send('User is already muted')
        sqlite_client.close()
        return

    sqlite_client.commit()
    sqlite_client.close()

    await warn(message, f'{member_reason[0].id} MUTE - {member_reason[1]}', client, action_name="muted")

    await asyncio.sleep(mute_time)
    await unmute(message, str(member_reason[0].id), client, silenced=True)

mute.command_data = {
    "syntax": "mute <member> | <duration<s|m|h|d|y>> [reason]",  
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

async def unmute(message, parameters, client, guild=False, silenced=False):
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

    for role in roles:
        if guild:
            role = message.get_role(role)
        else:
            role = message.guild.get_role(role)

        try:
            await member.add_roles(role)
        except discord.errors.Forbidden:
            if not silenced:
                await message.channel.send(f"Unable to re-give role: {role.name}")

    if guild:
        await member.remove_roles(message.get_role(configuration.MUTED_ROLE))
    else:
        await member.remove_roles(message.guild.get_role(configuration.MUTED_ROLE))

    if not silenced:
        await message.channel.send(f'Unmuted {member.name}#{member.discriminator} ({member.id})')

unmute.command_data = {
    "syntax": "unmute <member>",  
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

async def kick(message, parameters, client):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await warn(message, f"{member_reason[0].id} KICK - {member_reason[1]}", client, action_name="kicked")
        await message.guild.kick(member_reason[0], reason=member_reason[1])
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to kick")

kick.command_data = {
    "syntax": "kick <member> | [reason]",
    "aliases": ["kcik"],
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

async def ban(message, parameters, client):
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await warn(message, f"{member_reason[0].id} BAN - {member_reason[1]}", client, action_name="banned")
        await message.guild.ban(member_reason[0], reason=member_reason[1], delete_message_days=0)
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to ban")

ban.command_data = {
    "syntax": "ban <member> | [reason]",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION
}

# --------------------------------------------------#
# LEVEL COMMANDS #
# --------------------------------------------------#
async def rank(message, parameters, client):
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

    avatar = member.avatar_url_as(format=None, static_format='png', size=1024)

    rank_embed = discord.Embed(description=f"Rank for <@{member.id}>") \
        .add_field(name="Total XP:", value=user_xp[0]) \
        .add_field(name="Level:", value=(user_xp[1]-1)) \
        .add_field(name="Rank:", value="#" + str(user_rank[0])) \
        .add_field(name="XP until level up:", value=await levels.xp_needed_for_level(user_xp[1]) - user_xp[0]) \
        .set_author(name=f"{member.name}#{member.discriminator}", icon_url=avatar.__str__())
    # Internally, levels start at 1, but users want it to start at 0, so there is a fix for that

    await message.channel.send(embed=rank_embed)

rank.command_data = {
    "syntax": "rank",
    "aliases": ["wank"],
    "category": Category.LEVELING
}

async def leaderboards(message, parameters, client, first_execution=True, op=None, page_cache=0):
    try:
        page = int(parameters)
    except:
        # Human friendly compensation
        page = 1

    if first_execution:
        response = await message.channel.send(embed=discord.Embed(title="Loading"))
        await response.add_reaction("◀️")
        await response.add_reaction("▶️")

        sqlite_client = sqlite3.connect('bot_database.db')
        total_pages = sqlite_client.execute('''SELECT COUNT(*) FROM LEVELS''').fetchone()[0] // 10 + 1
        sqlite_client.close()

        await leaderboards(response, page, client, first_execution=False, op=message.author.id, page_cache=total_pages)
        return

    sqlite_client = sqlite3.connect('bot_database.db')
    data_list = sqlite_client.execute('''SELECT ID, LEVEL, XP FROM LEVELS ORDER BY XP DESC LIMIT 10 OFFSET :offset''',
                                          {"offset": (page - 1)*10}).fetchall()
    sqlite_client.close()

    lb_list = ''
    for index, data in enumerate(data_list):
        user = data[0]
        level = int(data[1]) - 1
        total_xp = data[2]
        lb_list += f"{(page - 1) * 10 + index + 1}: <@{user}> | Level: {level} | Total XP: {total_xp}\n"

    if not lb_list:
        lb_list = "No data on this page!"

    embed = discord.Embed(title="Leaderboard", description=lb_list).set_footer(text=f"Page: {page}/{page_cache}")
    await message.edit(embed=embed)

    def check(reaction, user):
        if op != user.id:
            return False

        if reaction.message.id != message.id:
            return False

        emoji = reaction.emoji

        valid = emoji == "◀️" or emoji == "▶️"
        if not valid:
            return False
        asyncio.get_running_loop().create_task(reaction.remove(user))
        nonlocal page
        if emoji == "◀️" and page > 1:
            page += -1
        elif emoji == "▶️" and page < page_cache:
            page += 1
        else:
            return False
        return True

    try:
        await client.wait_for('reaction_add', timeout=60.0, check=check)
        await leaderboards(message, page, client, first_execution=False, op=op, page_cache=page_cache)
    except asyncio.TimeoutError:
        await message.clear_reactions()

leaderboards.command_data = {
    "syntax": "leaderboards [page number]",
    "aliases": ["lb"],
    "category": Category.LEVELING
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
    # Set stuff to default values
    function.command_data["aliases"] = function.command_data.get("aliases", [])
    function.command_data["allowed_channels"] = function.command_data.get("allowed_channels", [])
    function.command_data["category"] = function.command_data.get("category", Category.OTHER)

    # Iterate through all aliases and add them as aliases
    for alias in function.command_data["aliases"]:
        command_aliases_dict[alias] = function

# Sort by priority for help
command_list.sort(key=lambda a: a.command_data["category"].value["priority"], reverse=True)