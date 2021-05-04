import discord

from command.command import Command, Category, Permission


class WhatDoesThisDo(Command):

    def __init__(self):
        super().__init__("whatdoesthisdo", "What does this do?", category=Category.DEVELOPMENT, required_permissions=Permission(required_roles=['744941527545020468'], permissions=discord.Permissions(**{'send_messages': True})))

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        for i in range(16):
            await message.channel.send(content=f"<@{message.author.id}>")
