import discord

from config import config
from command.command import Command, Parameter, Category


class Help(Command):
    def __init__(self):
        super().__init__("help", "Shows a command info or the list of the commands", ["commands", "?"], [
            Parameter("command")], category=Category.GENERAL)

    # noinspection PyMethodParameters
    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        command_list = Command.__subclasses__()
        command_list.sort(key=lambda a : a.category.value["priority"])

        if not parameters:
            last_category = ''
            category_commands: str = ''
            embed = discord.Embed(title="  ", description="  ")
            user = message.guild.me
            avatar = user.avatar_url_as(format=None, static_format='png', size=1024)
            embed.set_author(name=user.name, icon_url=avatar.__str__())
            embed.set_footer(text=f"Version: {config['version']}")

            for _cmd in command_list:
                cmd: Command = _cmd()
                name = cmd.command
                arguments = ''.join(f" <{argument.identifier}>" if argument.required \
                    else f" [{argument.identifier}]" \
                    for argument in cmd.parameters)

                if last_category != cmd.category and last_category != '' and command_list[
                    len(command_list) - 1] != _cmd:
                    embed.add_field(name=last_category, value=category_commands, inline=False)
                    last_category = cmd.category.value["friendly_name"]
                    category_commands = ''
                    category_commands += f"`{config['prefix']}{name}{arguments}` | {cmd.description}\n"
                elif last_category != cmd.category and last_category != '' and command_list[
                    len(command_list) - 1] == _cmd:
                    embed.add_field(name=last_category, value=category_commands, inline=False)
                    last_category = cmd.category.value["friendly_name"]
                    category_commands = ''
                    category_commands += f"`{config['prefix']}{name}{arguments}` | {cmd.description}\n"
                    embed.add_field(name=last_category, value=category_commands, inline=False)
                elif last_category is None or last_category == '':
                    last_category = cmd.category.value["friendly_name"]
                    category_commands += f"`{config['prefix']}{name}{arguments}` | {cmd.description}\n"
                elif command_list[len(command_list) - 1] == _cmd:
                    category_commands += f"`{config['prefix']}{name}{arguments}` | {cmd.description}\n"
                    embed.add_field(name=cmd.category.value["friendly_name"], value=category_commands, inline=False)
                else:
                    category_commands += f"`{config['prefix']}{name}{arguments}` | {cmd.description}\n"
        else:
            def filter_commands(command_):
                return command_().command == parameters or parameters in command_().alias

            possible_commands = filter(filter_commands, command_list)
            cmd = possible_commands.__next__()()
            name = cmd.command
            arguments = ''.join(f" <{argument.identifier}>" if argument.required \
                else f" [{argument.identifier}]" \
                for argument in cmd.parameters)

            all_alias = ', '.join(alias for alias in cmd.alias)

            embed = discord.Embed(title=f"{name}", description="  ")
            user = message.guild.me
            avatar = user.avatar_url_as(format=None, static_format='png', size=1024)
            embed.set_author(name=user.name, icon_url=avatar.__str__())
            embed.set_footer(text=f"Version: {config['version']}")
            embed.add_field(name="Syntax", value=f"`{config['prefix']}{name}{arguments}`", inline=True)
            if all_alias != ', ':
                embed.add_field(name="Alias", value=f"`{all_alias}`", inline=True)

            permissions_text = ''
            permissions_text += ', '.join(f'{message.guild.get_role(int(role)).mention}'\
                for role in cmd.required_permissions.required_roles)

            for flag in cmd.required_permissions.permissions:
                if flag[1]:
                    permissions_text += f"{str(flag[0]).upper()}"

            if not permissions_text:
                permissions_text = "None"

            embed.add_field(name="Required Permissions", value=f"{permissions_text}", inline=True)
        await message.channel.send(embed=embed)
