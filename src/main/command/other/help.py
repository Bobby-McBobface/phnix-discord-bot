import discord

import main
from command.command import Command, Parameter, Category


class Help(Command):
    def __init__(self):
        super().__init__("help", "Shows a command info or the list of the commands", ["commands", "?"], [
            Parameter("command")], category=Category.GENERAL)

    # noinspection PyMethodParameters
    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        command_list = Command.__subclasses__()
        command_list.sort(key=main.sort_commands)

        if not parameters or parameters == '':
            last_category = ''
            category_commands: str = ''
            embed = discord.Embed(title="  ", description="  ")
            user = message.guild.me
            avatar = user.avatar_url_as(format=None, static_format='png', size=1024)
            embed.set_author(name=user.name, icon_url=avatar.__str__())
            embed.set_footer(text=f"Version: {main.config['version']}")

            for _cmd in command_list:
                cmd: Command = _cmd()
                name = cmd.command
                arguments = ''
                for argument in cmd.parameters:
                    if argument.required:
                        arguments += f" <{argument.identifier}>"
                    elif not argument.required:
                        arguments += f" [{argument.identifier}]"

                if last_category != cmd.category and last_category != '' and command_list[len(command_list) - 1] != _cmd:
                    embed.add_field(name=last_category, value=category_commands, inline=False)
                    last_category = cmd.category.value.friendlyName
                    category_commands = ''
                    category_commands += f"`{main.config['prefix']}{name}{arguments}` | {cmd.description}\n"
                elif last_category != cmd.category and last_category != '' and command_list[len(command_list) - 1] == _cmd:
                    embed.add_field(name=last_category, value=category_commands, inline=False)
                    last_category = cmd.category.value.friendlyName
                    category_commands = ''
                    category_commands += f"`{main.config['prefix']}{name}{arguments}` | {cmd.description}\n"
                    embed.add_field(name=last_category, value=category_commands, inline=False)
                elif last_category is None or last_category == '':
                    last_category = cmd.category.value.friendlyName
                    category_commands += f"`{main.config['prefix']}{name}{arguments}` | {cmd.description}\n"
                elif command_list[len(command_list) - 1] == _cmd:
                    category_commands += f"`{main.config['prefix']}{name}{arguments}` | {cmd.description}\n"
                    embed.add_field(name=cmd.category.value.friendlyName, value=category_commands, inline=False)
                else:
                    category_commands += f"`{main.config['prefix']}{name}{arguments}` | {cmd.description}\n"

            await message.channel.send(embed=embed)
