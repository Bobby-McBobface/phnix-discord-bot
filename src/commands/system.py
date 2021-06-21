import discord
from commands import CommandSyntaxError, Category, command, command_list, command_aliases_dict
import configuration

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
    exec(parameters, globals(), locals())

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
    await ping_message.edit(content=f'Pong! Round trip: {end_time-start_time}ms | Websocket: {str(client.latency*100)[:3]}ms', suppress=True)

command_list_already_preprocessed = False

@command({
    "syntax": "help [command]",
    "aliases": ["?"],
    "category": Category.SYSTEM,
    "description": "Shows help on commands"
})
async def help(message: discord.Message, parameters: str, client: discord.Client) -> None:
    """Help command - Lists all commands, or gives info on a specific command."""

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
