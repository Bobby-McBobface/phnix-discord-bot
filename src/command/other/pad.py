import discord

from command.command import Command, Category, Permission, CommandSyntaxError, Parameter
from config import config


class Pad(Command):

    def __init__(self):
        super().__init__("pad", "Spaces out your text", parameters=[Parameter("text", True)], category=Category.OTHER)

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        """Spaces out your text"""
        if not parameters:
            raise CommandSyntaxError
        else:
            await message.channel.send(" ".join(parameters))
