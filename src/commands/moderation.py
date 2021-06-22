from ast import literal_eval
import asyncio
import sqlite3
from time import time

import discord
from discord import embeds
import configuration
import util
from commands import Category, CommandSyntaxError, command
import database_handle

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
    
    database_handle.cursor.execute('''INSERT INTO WARNS (ID, REASON, TIMESTAMP) \
    VALUES(:member_id, :reason, :time)''',
                            {'member_id': member_reason[0].id, 'reason': str(member_reason[1]),
                            'time': round(time())})
    database_handle.client.commit()
    
    # Send a message to the channel that the command was used in
    warn_embed = discord.Embed(title=action_name.title(),
                                description=member_reason[0].mention) \
                        .add_field(name="Reason", value=member_reason[1])
    
    await message.channel.send(embed=warn_embed)
    try:
        # DM user
        #await member_reason[0].send(content=f"You have been **{action_name}** in {message.guild.name}!", embed=warn_embed)
        pass
    except discord.errors.Forbidden:
        await message.channel.send("Unable to DM user")

@command({
    "syntax": "warns <member>",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.MODERATION,
    "description": "List the warns of a user"
})
async def warns(message: discord.Message, parameters: str, client: discord.Client, op:discord.Member=None, first_execution: bool=True, page:int=0, total_warns_cache:int=0) -> None:
    if first_execution:
        member = util.get_member_by_id_or_name(message, parameters)

        if member is None:
            user_id = util.try_get_valid_user_id(parameters)
            if not user_id:
                raise CommandSyntaxError("You must specify a valid user!")

        else:
            user_id = member.id



        total_warns = database_handle.cursor.execute(
            '''SELECT COUNT(*) FROM WARNS WHERE ID=:member_id''', {"member_id": user_id}).fetchone()[0]

        if total_warns == 0:
            await message.channel.send("User has no warns.")
            return

        response = await message.channel.send(embed=discord.Embed(title="Loading"))
        await response.add_reaction("◀️")
        await response.add_reaction("▶️")
    
        await warns(response, user_id, client, op=message.author.id, first_execution=False, page=0, total_warns_cache=total_warns)
        return
    
    warn_list = database_handle.cursor.execute('''SELECT REASON, TIMESTAMP FROM WARNS WHERE ID = :member_id LIMIT 10 OFFSET :offset''',
                                    {'member_id': parameters, "offset": page * 10}).fetchall()
    
    warn_text = ''
    timestamp_text = ''

    for warn in warn_list:
        warn_text += str(warn[0]) + '\n'
        timestamp_text += f"<t:{warn[1]}:R> \n"

    warn_embed = discord.Embed(title=f"Warns. Total of {total_warns_cache}", description=f"<@{parameters}>") \
                        .add_field(name="Reason", value=warn_text) \
                        .add_field(name="Timestamp", value=timestamp_text) \
                        .set_footer(text=f"Page: {page+1}/{total_warns_cache//10+1}")

    await message.edit(embed=warn_embed)

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
        if emoji == "◀️" and page > 0:
            page += -1
        elif emoji == "▶️" and page < total_warns_cache // 10:
            page += 1
        else:
            return False
        return True

    try:
        await client.wait_for('reaction_add', timeout=30.0, check=check)
        await warns(message, parameters, client, first_execution=False, op=op, page=page, total_warns_cache=total_warns_cache)
    except asyncio.TimeoutError:
        await message.clear_reactions()

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
    
    warn = database_handle.cursor.execute('''SELECT REASON FROM WARNS WHERE TIMESTAMP=:timestamp AND ID=:id''',
                                    {"timestamp": member_reason[1], "id": member_reason[0].id}).fetchone()

    if warn is not None:
        await message.channel.send(f"Deleting warn from {member_reason[0].name}#{member_reason[0].discriminator} ({member_reason[0].id}) about {warn[0]}")
    else:
        await message.channel.send("No warn found")
        return

    database_handle.cursor.execute('''DELETE FROM WARNS WHERE TIMESTAMP=:timestamp AND ID=:id''',
                            {"timestamp": member_reason[1], "id": member_reason[0].id})
    database_handle.client.commit()
    

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
    
    try:
        database_handle.cursor.execute('''INSERT INTO MUTES (ID, TIMESTAMP, ROLES) \
        VALUES(:member_id, :timestamp, :roles) ''',
                                {'member_id': member_reason[0].id, 'timestamp': round(time()) + mute_time,
                                'roles': str([role.id for role in roles])})
    except sqlite3.IntegrityError:
        await message.channel.send('User is already muted')
        return

    database_handle.client.commit()
    
    # Remove all roles
    forbidden_role_list = []
    for role in roles:
        if role.id != configuration.MUTED_ROLE:
            try:
                await member_reason[0].remove_roles(role)
            except discord.errors.Forbidden:
                forbidden_role_list.append(role)

    if forbidden_role_list:
        await message.channel.send(f"Unable to remove roles: {forbidden_role_list}")

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
        member = util.get_member_by_id_or_name(message, parameters)

    if member is None:
        user_id = util.try_get_valid_user_id(parameters)
        if not user_id:
            raise CommandSyntaxError("You must specify a valid user!")

    else:
        user_id = member.id

    roles = database_handle.cursor.execute('''SELECT ROLES FROM MUTES WHERE ID=:member_id''',
                                    {'member_id': user_id}).fetchone()
        
    database_handle.cursor.execute('''DELETE FROM MUTES WHERE ID=:member_id''',
                        {'member_id': user_id})
    database_handle.client.commit()
    
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
    forbidden_roles_list = []

    for role in roles:
        if guild:
            role = message.get_role(role)
        else:
            role = message.guild.get_role(role)

        try:
            await member.add_roles(role)
        except:
            forbidden_roles_list.append(role)

    if not silenced and forbidden_roles_list:
        await message.channel.send(f"Unable to re-give roles: {forbidden_roles_list}")

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
    
    if not message.guild.me.guild_permissions.kick_members:
        await message.channel.send("I don't have permissions to kick.")
        return

    if message.guild.me.top_role <= member_reason[0].top_role:
        await message.channel.send("I am not high enough in the role hierarchy")
        return

    # if message.author.top_role <= member_reason[0].top_role:
    #     await message.channel.send("You are not high enough in the role hierarchy.")
    #     return

    await warn(message, f"{member_reason[0].id} KICK - {member_reason[1]}", client, action_name="kicked")
    await message.guild.kick(member_reason[0], reason=member_reason[1])

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
    
    if not message.guild.me.guild_permissions.kick_members:
        await message.channel.send("I don't have permissions to kick.")
        return

    if message.guild.me.top_role <= member_reason[0].top_role:
        await message.channel.send("I am not high enough in the role hierarchy.")
        return

    # if message.author.top_role <= member_reason[0].top_role:
    #     await message.channel.send("You are not high enough in the role hierarchy.")
    #     return

    await warn(message, f"{member_reason[0].id} BAN - {member_reason[1]}", client, action_name="banned")
    await message.guild.ban(member_reason[0], reason=member_reason[1], delete_message_days=0)

