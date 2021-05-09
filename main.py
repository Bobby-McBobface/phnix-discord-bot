import discord
from time import time
import asyncio
import sqlite3

import commands
import configuration
import levels
import util
import youtube
import twitch


class PhnixBotClient(discord.Client):
    async def on_ready(self):
        """Runs when the bot is operational"""
        print('PhnixBot is ready')
        await self.remute_on_startup()
        asyncio.ensure_future(levels.clear_chatted_loop())
        asyncio.ensure_future(youtube.youtube(self))
        asyncio.ensure_future(twitch.twitch(self))

    async def on_member_join(self, member):
        welcome_channel = self.get_channel(configuration.WELCOME_CHANNEL)
        await welcome_channel.send(configuration.welcome_msg.format("<@" + str(member.id) + ">"))

        # Check if member is muted and give appropriate role:
        muted = await util.check_if_muted(member)

        if muted and muted[1] - time() > 0:
            await member.add_roles(member.guild.get_role(configuration.MUTED_ROLE))
            await asyncio.sleep(muted[1] - time())
            await commands.unmute(member.guild, muted[0], self, guild=True, silenced=True)
        elif muted and muted[1] - time() < 0:
            await commands.unmute(member.guild, muted[0], self, guild=True, silenced=True)

        # Regive level roles
        sqlite_client = sqlite3.connect('bot_database.db')
        try:
            level = sqlite_client.execute('''SELECT LEVEL FROM LEVELS WHERE ID=:member_id''',
                                          {'member_id': member.id}).fetchone()[0]
        except:
            level = 0

        await levels.give_level_up_roles(member, level)

    async def on_member_remove(self, member):
        farewell_message = configuration.farewell_msg.format(member)
        farewell_message = discord.utils.escape_markdown(farewell_message) # Escape Discord markdown formatting, e.g. so underscores in their name doesn't turn into italics
        farewell_channel = self.get_channel(configuration.FAREWELL_CHANNEL)
        await farewell_channel.send(farewell_message)

    async def on_member_update(self, before, after):
        # Check if their nick is invisible
        if (await util.check_if_string_invisible(after.display_name)):
            # Their nickname is invisible! Change it
            new_nick = None if not (await util.check_if_string_invisible(after.name)) \
                else str(after.id)  # idk lol set it to their user id I guess
            await after.edit(nick=new_nick, reason="Invisible nickname detected")

    async def remute_on_startup(self):
        sqlite_client = sqlite3.connect('bot_database.db')
        mute_list = sqlite_client.execute(
            '''SELECT ID, TIMESTAMP FROM MUTES''').fetchall()

        # Cheap fix for now since this is used in 1 server
        guild = self.get_guild(configuration.GUILD_ID)
        for mute in mute_list:
            if mute[1] - time() > 0:
                await asyncio.sleep(mute[1] - time())
                await commands.unmute(guild, mute[0], self, guild=True, silenced=True)
            elif mute[1] - time() < 0:
                await commands.unmute(guild, mute[0], self, guild=True, silenced=True)

    async def on_message(self, message):
        """Runs every time the bot notices a message being sent anywhere."""

        # Ignore bot accounts
        if message.author.bot:
            return

        # EXP/leveling system
        if message.channel.id not in configuration.DISALLOWED_XP_GAIN:
            await levels.add_exp(message.author, message)

        # COMMANDS: Check if it has our command prefix, or starts with a mention of our bot
        command_text = await util.check_for_and_strip_prefixes(
            message.content,
            (configuration.PREFIX, self.user.mention, f"<@!{self.user.id}>"))

        # If there was a command prefix...
        if command_text is not None and command_text != '':

            # Split the command into 2 parts, command name and parameters
            split_command_text = command_text.split(maxsplit=1)

            command_name = split_command_text[0].lower()

            if len(split_command_text) == 2:
                # Theres 2 elements, so there must be a name and parameters
                parameters = split_command_text[1]
                # Remove trailing whitespaces
                parameters = parameters.strip()
            else:
                # No paramaters specified
                parameters = None

            try:
                # Get the command's function
                command_function = commands.command_aliases_dict[command_name]
            except KeyError:
                # There must not be a command by that name.
                return

            # We got the command's function!

            # bot-nether check
            if message.guild.get_role(configuration.MODERATOR_ROLE) not in message.author.roles \
                    and message.guild.id == configuration.GUILD_ID:
                # Mod bypass and other server bypass

                if message.channel.id not in command_function.command_data["allowed_channels"] \
                        and message.channel.id not in configuration.ALLOWED_COMMAND_CHANNELS:

                    await message.channel.send(f"Please use <#{configuration.DEFAULT_COMMAND_CHANNEL}> for bot commands!")
                    return

            requirements = command_function.command_data.get(
                "role_requirements")

            # Do role checks
            if requirements:
                # its not an @everyone command..
                if not requirements.intersection([role.id for role in message.author.roles]):
                    # User does not have permissions to execute that command.
                    roles_string = " or ".join([f"`{message.guild.get_role(role_id).name}`" for role_id in
                                                command_function.command_data['role_requirements'] if
                                                message.guild.get_role(role_id) != None])
                    await message.channel.send(f"You don't have permission to do that! You need {roles_string}.")
                    return

            # Run the found function
            try:
                await command_function(message, parameters, self)

            except commands.CommandSyntaxError as err:
                # If the command raised CommandSyntaxError, send some information to the user:
                error_details = f": {str(err)}\n" if str(
                    err) != "" else ". "  # Get details from the exception, and format it
                # Get command syntax from the function
                error_syntax = command_function.command_data['syntax']
                # Put it all together
                error_message = f"Invalid syntax{error_details}Usage: `{error_syntax}`"
                await message.channel.send(error_message)


if __name__ == '__main__':
    with open('env/token') as file:
        token = file.read()

    intents = discord.Intents.default()
    intents.members = True
    intents.typing = False
    intents.presences = False

    allowed_mentions = discord.AllowedMentions(
        everyone=False,
        roles=False,
        users=True
    )

    client = PhnixBotClient(
        intents=intents, allowed_mentions=allowed_mentions)

    client.run(token)

    print('PhnixBot Killed')
