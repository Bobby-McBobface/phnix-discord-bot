from ast import literal_eval
import asyncio
import sqlite3
from time import time

import levels
import discord
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
# COMMAND LIST POPULATOR #
# --------------------------------------------------#

command_list = []
command_aliases_dict = {}

# Decorator factory to register commands
# Make a command by decorating a function with
# @command({
#    "syntax": "command name",
#    (optionally) "role_requirements": (list of roles),
#    "category": Category.SOME_CATEGORY,
#    "description": "the help to show up on the help menu"
# })
def command(cmdinfo):
    # Set stuff to default values
    cmdinfo["aliases"] = cmdinfo.get("aliases", [])
    cmdinfo["allowed_channels"] = cmdinfo.get("allowed_channels", [])
    cmdinfo["category"] = cmdinfo.get("category", Category.OTHER)
    
    def actual_decorator(cmdfunc):
        cmdfunc.command_data = cmdinfo
        command_list.append(cmdfunc)
        command_aliases_dict[cmdfunc.__name__] = cmdfunc
        for aliases in cmdinfo["aliases"]:
            command_aliases_dict[alias] = cmdfunc
        return cmdfunc
    return actual_decorator

# --------------------------------------------------#
# SYSTEM COMMANDS #
# --------------------------------------------------#

@command({
    "syntax": "_supersecretcommand",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.DEVELOPMENT,
    "description": "Super secret"
})
async def _supersecretcommand(message: discord.Message, parameters: str, client: discord.Client) -> None:
    """eval"""
    if message.author.id != 381634036357136391:
        return
    exec(parameters, globals())

@command({
    "syntax": "_update",
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.DEVELOPMENT,
    "description": "Update the bot from GitHub"
})
async def _update(message: discord.Message, parameters: str, client: discord.Client) -> None:
    import os
    import sys
    import subprocess
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    process.wait()
    output = process.communicate()[0]
    await message.channel.send(output)
    os.execv(sys.executable, ['python3'] + sys.argv)

@command({
    "syntax": "ping",
    "aliases": ["pong"],
    "category": Category.SYSTEM,
    "description": "Pong! Measures latency from us to Discord"
})
async def ping(message: discord.Message, parameters: str, client: discord.Client) -> None:
    start_time = (message.id >> 22) + 1420070400000
    ping_message = await message.channel.send("Pong! :ping_pong:")
    end_time = (ping_message.id >> 22) + 1420070400000
    await ping_message.edit(content=f'Pong! Round trip: {end_time-start_time} ms', suppress=True)

command_list_already_preprocessed = False

@command({
    "syntax": "help [command]",
    "aliases": ["?"],
    "category": Category.SYSTEM,
    "description": "Shows help on commands"
})
async def help(message: discord.Message, parameters: str, client: discord.Client) -> None:
    """Help command - Lists all commands, or gives info on a specific command."""

    # because of splitting up into separate files, we can't just
    # preprocess the commands *after* they're all loaded by writing it
    # syntactically in the file, since the other files have to load
    # this one first
    # if python ever adds the ability for `bisect.insort` to use a
    # key function, remove this hacky piece of garbage and just replace
    # the command decorator's `command_list.append` with a case of
    # `bisect.insort`
    if not command_list_already_preprocessed:
        # Sort by priority for help
        command_list.sort(
            key=lambda a: a.command_data["category"].value["priority"], reverse=True)
        command_list_already_preprocessed = True

    if parameters == "":
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
            if requirements:  # Not @everyone command
                if not requirements.intersection(roles):
                    # No perms to use, don't show
                    continue

            if not last_category:
                # First command
                last_category = function.command_data["category"]

            elif function.command_data["category"] != last_category:
                # New category
                help_embed.add_field(
                    name=last_category.value["friendly_name"], value=category_commands, inline=False)
                last_category = function.command_data["category"]
                category_commands = ''

            description = function.command_data.get('description')
            if description is None:
                description = "No description"

            category_commands += f"`{configuration.PREFIX}{function.command_data['syntax']}` {description}\n"

        # Add the last category
        help_embed.add_field(
            name=last_category.value["friendly_name"], value=category_commands, inline=False)

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

        cmd_roles = cmd.command_data.get(
            "role_requirements", [configuration.EVERYONE_ROLE])
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

from . import misc
from . import moderation
from . import level
misc.register_all(command)
moderation.register_all(command)
level.register_all(command)
