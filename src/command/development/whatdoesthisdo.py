import discord

from command.command import Command, Category, Permission
from config import config


class WhatDoesThisDo(Command):

    def __init__(self):
        super().__init__("whatdoesthisdo", "What does this do?", category=Category.DEVELOPMENT, required_permissions=Permission(required_roles={config["moderatorRole"]}))

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        await message.channel.send(content=f"<@{message.author.id}>")
