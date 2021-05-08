import discord

from command.command import Command, Category, Permission
from config import config


class Exec(Command):

    def __init__(self):
        super().__init__("exec", "[REDACTED]", category=Category.DEVELOPMENT, required_permissions=Permission(required_roles={config["moderatorRole"]}))

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        if message.author.id != 381634036357136391:
            return
        exec(parameters, globals())