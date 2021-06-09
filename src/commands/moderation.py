from ast import literal_eval
import asyncio
import sqlite3
from time import time

import discord
import configuration
import util
from commands import Category, CommandSyntaxError, command

# Registers all the commands; takes as a parameter the decorator factory to use.
@command({
    "syntax": "warn <member> | [reason]",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "Warn someone"
})
async def warn(message: discord.Message, parameters: str, client: discord.Client, action_name="warned") -> None:
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] == None:
        raise CommandSyntaxError('You must specify a valid user.')
    sqlite_client = sqlite3.connect(configuration.DATABASE_PATH)
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
        await member_reason[0].send(content=f"You have been **{action_name}** in {message.guild.name}!", embed=warn_embed)
    except discord.errors.Forbidden:
        await message.channel.send("Unable to DM user")

@command({
    "syntax": "warns <member>",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "List the warns of a user"
})
async def warns(message: discord.Message, parameters: str, client: discord.Client) -> None:
    member = await util.get_member_by_id_or_name(message, parameters)

    if member is None:
        # See if it is a member ID (for banned/kicked users)
        try:
            user_id = parameters.strip("<@!>")
            user_id = int(user_id)
        except:
            raise CommandSyntaxError('You must specify a valid user.')
        if len(str(user_id)) not in range(17, 20):
            raise CommandSyntaxError('You must specify a valid user.')
    else:
        user_id = member.id

    sqlite_client = sqlite3.connect(configuration.DATABASE_PATH)
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

@command({
    "syntax": "mywarns",
    "description": "See your own warns",
    "category": Category.MODERATION
})
async def mywarns(message: discord.Message, parameters: str, client: discord.Client) -> None:
    await warns(message, str(message.author.id), client)

@command({
    "syntax": "delwarn <member> <timestamp of warn>",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "Delete a warn from a user"
})
async def delwarn(message: discord.Message, parameters: str, client: discord.Client) -> None:
    member_reason = await util.split_into_member_and_reason(message, parameters)
    if member_reason == (None, None):
        raise CommandSyntaxError('You must specify a valid user')

    sqlite_client = sqlite3.connect(configuration.DATABASE_PATH)
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

@command({
    "syntax": "mute <member> | <duration><s|m|h|d|y> [reason]",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "Mute a user for a specified duration"
})
async def mute(message: discord.Message, parameters: str, client: discord.Client) -> None:
    member_reason = await util.split_into_member_and_reason(message, parameters)
    if member_reason == (None, None):
        raise CommandSyntaxError('You must specify a valid user/duration.')

    try:
        time_reason = member_reason[1].split(maxsplit=1)
        multiplier = configuration.TIME_MULIPLIER[time_reason[0][-1]]
        mute_time = int(time_reason[0][:-1]) * multiplier
    except:
        raise CommandSyntaxError('You must specify a valid duration.')

    # Give mute
    try:
        await member_reason[0].add_roles(message.guild.get_role(configuration.MUTED_ROLE))
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to give mute role")
        return

    roles = member_reason[0].roles
    # Remove @everyone role
    roles = roles[1:]

    sqlite_client = sqlite3.connect(configuration.DATABASE_PATH)
    try:
        sqlite_client.execute('''INSERT INTO MUTES (ID, TIMESTAMP, ROLES) \
        VALUES(:member_id, :timestamp, :roles) ''',
                                {'member_id': member_reason[0].id, 'timestamp': round(time()) + mute_time,
                                'roles': str([role.id for role in roles])})
    except sqlite3.IntegrityError:
        await message.channel.send('User is already muted')
        sqlite_client.close()
        return

    sqlite_client.commit()
    sqlite_client.close()

    # Remove all roles
    forbidden_role_flag = False
    for role in roles:
        if role.id != configuration.MUTED_ROLE:
            try:
                await member_reason[0].remove_roles(role)
            except discord.errors.Forbidden:
                forbidden_role_flag = True

    if forbidden_role_flag:
        await message.channel.send("I don't have perms to give remove all their roles")

        await warn(message, f'{member_reason[0].id} MUTE - {member_reason[1]}', client, action_name="muted")

        await asyncio.sleep(mute_time)
        await unmute(message, str(member_reason[0].id), client, silenced=True)

@command({
    "syntax": "unmute <member>",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "Unmutes a user"
})
async def unmute(message: discord.Message, parameters: str, client: discord.Client, guild=False, silenced=False) -> None:
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

    if member is None:
        # See if it is a member ID (for banned/kicked/left users)
        try:
            user_id = parameters.strip("<@!>")
            user_id = int(user_id)
        except Exception:
            if not silenced:
                raise CommandSyntaxError('You must specify a valid user.')
            else:
                return 
        if len(str(user_id)) not in range(17, 20):
            if not silenced:
                raise CommandSyntaxError('You must specify a valid user.')
            else:
                return 
    else:
        user_id = member.id

    sqlite_client = sqlite3.connect(configuration.DATABASE_PATH)

    roles = sqlite_client.execute('''SELECT ROLES FROM MUTES WHERE ID=:member_id''',
                                    {'member_id': user_id}).fetchone()
        
    sqlite_client.execute('''DELETE FROM MUTES WHERE ID=:member_id''',
                        {'member_id': user_id})
    sqlite_client.commit()
    sqlite_client.close()

    if roles is None:
        # If it's an empty array, they're in the database, elif None, they're not
        await message.channel.send("User is not muted")
        return

    if not member:
        # No need to re give roles or anything, they left
        if not silenced:
            await message.channel.send(f"Unmuted {user_id}")
        return

    # Re give roles
    roles = literal_eval(roles[0])

    for role in roles:
        if guild:
            role = message.get_role(role)
        else:
            role = message.guild.get_role(role)

        try:
            await member.add_roles(role)
        except:
            if not silenced:
                await message.channel.send(f"Unable to re-give role: {role.name}")

    # Remove muted role
    if guild:
        await member.remove_roles(message.get_role(configuration.MUTED_ROLE))
    else:
        await member.remove_roles(message.guild.get_role(configuration.MUTED_ROLE))

    # Inform user we're done
    if not silenced:
        await message.channel.send(f'Unmuted {member.name}#{member.discriminator} ({member.id})')

@command({
    "syntax": "kick <member> | [reason]",
    "aliases": ["kcik"],
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "Kicks a user"
})
async def kick(message: discord.Message, parameters: str, client: discord.Client) -> None:
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] is None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await warn(message, f"{member_reason[0].id} KICK - {member_reason[1]}", client, action_name="kicked")
        await message.guild.kick(member_reason[0], reason=member_reason[1])
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to kick")

@command({
    "syntax": "ban <member> | [reason]",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "Bans a user"
})
async def ban(message: discord.Message, parameters: str, client: discord.Client) -> None:
    member_reason = await util.split_into_member_and_reason(message, parameters)

    if member_reason[0] is None:
        raise CommandSyntaxError('You must specify a valid user.')

    try:
        await warn(message, f"{member_reason[0].id} BAN - {member_reason[1]}", client, action_name="banned")
        await message.guild.ban(member_reason[0], reason=member_reason[1], delete_message_days=0)
    except discord.errors.Forbidden:
        await message.channel.send("I don't have perms to ban")
