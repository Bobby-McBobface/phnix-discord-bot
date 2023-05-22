import asyncio
import sys
import traceback
from time import time

import discord

import commands
import configuration
import database_handle
import levels
import logger
import twitch
import util
import youtube


class PhnixBotClient(discord.Client):
    DEBUG_SPY_MODE = False

    async def on_ready(self) -> None:
        """Runs when the bot is operational"""
        print('PhnixBot is ready')

        asyncio.get_running_loop().create_task(levels.clear_chatted_loop())
        asyncio.get_running_loop().create_task(youtube.youtube(self))
        asyncio.get_running_loop().create_task(twitch.twitch(self))
        await self.remute_on_startup()

    async def on_error(self, event_method, *args, **kwargs) -> None:
        try:
            print(f'Ignoring exception in {event_method}', file=sys.stderr)
            error = traceback.format_exc()
            print(error)
            await logger.log_error(error, self)
        except Exception as e:
            print("Caught error in on_error:", e)

    async def on_member_join(self, member) -> None:
        welcome_channel = self.get_channel(configuration.WELCOME_CHANNEL)
        await welcome_channel.send(configuration.WELCOME_MSG.format("<@" + str(member.id) + ">"))

        # Check if member is muted and give appropriate role:
        muted = database_handle.cursor\
            .execute('''SELECT ID, TIMESTAMP FROM MUTES WHERE ID=:member_id''',
                                               {'member_id': member.id, }).fetchone()

        if muted and muted[1] - time() > 0:
            await member.add_roles(member.guild.get_role(configuration.MUTED_ROLE))
            return

        # Regive level roles
        try:
            level = database_handle.cursor.execute('''SELECT LEVEL FROM LEVELS WHERE ID=:member_id''',
                                                   {'member_id': member.id}).fetchone()[0]
        except:
            # No level, first join
            return

        await levels.give_level_up_roles(member, level)

    async def on_member_remove(self, member) -> None:
        farewell_message = configuration.FAREWELL_MSG.format(member)
        # Escape Discord markdown formatting, e.g. so underscores
        # in their name doesn't turn into italics
        farewell_message = discord.utils.escape_markdown(farewell_message)
        farewell_channel = self.get_channel(configuration.FAREWELL_CHANNEL)
        await farewell_channel.send(farewell_message)

    @staticmethod
    async def on_member_update(after) -> None:
        # Check if their nick is invisible
        if util.check_if_string_invisible(after.display_name):
            # Their nickname is invisible! Change it
            new_nick = None if not (util.check_if_string_invisible(after.name)) \
                else str(after.id)  # idk lol set it to their user id I guess
            await after.edit(nick=new_nick, reason="Invisible nickname detected")

    async def _remute_on_startup(self, guild, mute) -> None:
        await asyncio.sleep(mute[1] - time())
        await commands.command_aliases_dict["unmute"]\
            (guild, str(mute[0]), self, guild=True, silenced=True)

    async def remute_on_startup(self) -> None:
        mute_list = database_handle.cursor.execute(
            '''SELECT ID, TIMESTAMP FROM MUTES''').fetchall()

        # Cheap fix for now since this is used in 1 server
        guild = self.get_guild(configuration.GUILD_ID)

        for mute in mute_list:
            if mute[1] - time() > 0:
                asyncio.get_event_loop().create_task(self._remute_on_startup(guild, mute))
            elif mute[1] - time() < 0:
                await commands.command_aliases_dict["unmute"]\
                    (guild, str(mute[0]), self, guild=True, silenced=True)

    async def on_message(self, message) -> None:
        """Runs every time the bot notices a message being sent anywhere."""

        if self.DEBUG_SPY_MODE:
            print(message.content)

        # Ignore bot accounts
        if message.author.bot or isinstance(message.channel) != discord.channel.TextChannel:
            return

        # if await automod.automod(message, self):
        # If automod returns True, message violated rules
        # return

        # EXP/leveling system
        if message.channel.id not in configuration.DISALLOWED_XP_GAIN:
            await levels.add_exp(message.author, message)

        # COMMANDS: Check if it has our command prefix, or starts with a mention of our bot
        command_text = ''
        # Find the command_text from stripping a command prefix
        for prefix in (configuration.PREFIX, self.user.mention, f"<@!{self.user.id}>"):
            if message.content.startswith(prefix):
                command_text = message.content[len(prefix):].lstrip()
                break

        # If there was a command prefix and command text found...
        if command_text != '':

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
                parameters = ""

            try:
                # Get the command's function
                command_function = commands.command_aliases_dict[command_name]
            except KeyError:
                # There must not be a command by that name.
                return

            # We got the command's function!

            # bot-nether check
            if not util.check_mod_or_test_server(message):
                # Mod bypass and other server bypass

                if message.channel.id not in command_function.command_data["allowed_channels"] \
                        and message.channel.id not in configuration.ALLOWED_COMMAND_CHANNELS:
                    error_message = await message.channel.send(
                        f"Please use <#{configuration.DEFAULT_COMMAND_CHANNEL}> for bot commands!")
                    await asyncio.sleep(configuration.DELETE_ERROR_MESSAGE_TIME)
                    await error_message.delete()
                    return

            requirements = command_function.command_data.get(
                "role_requirements")

            # Do role checks
            if requirements:
                # its not an @everyone command..
                if not requirements.intersection([role.id for role in message.author.roles]):
                    # User does not have permissions to execute that command.
                    roles_string = " or "\
                        .join([f"`{message.guild.get_role(role_id).name}`" for role_id in
                                                command_function.command_data['role_requirements'] if
                                                message.guild.get_role(role_id) != None])
                    error_message = await message.channel.send(
                        f"You don't have permission to do that! You need {roles_string}.")
                    await asyncio.sleep(configuration.DELETE_ERROR_MESSAGE_TIME)
                    await error_message.delete()
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
                error_text = f"Invalid syntax{error_details}Usage: `{error_syntax}`"
                error_message = await message.channel.send(error_text)
                await asyncio.sleep(configuration.DELETE_ERROR_MESSAGE_TIME)
                await error_message.delete()

            except discord.errors.Forbidden as err:
                # Intercept the error, adding more context to it.
                # (Hopefully the error message Python shows should
                # show the original traceback?)
                raise RuntimeError(
                    f"'{str(err)}' when running a command function.\
                    \nTriggering message URL: {message.jump_url}\
                    \n Command text: {repr(command_text)}") from err


if __name__ == '__main__':
    with open('env/token', encoding='utf-8') as file:
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
    database_handle.client.close()
