from typing import Union

import discord

from command.command import Command, Category


class WhatDoesThisDo(Command):

    def __init__(self):
        super().__init__("whatdoesthisdo", "What does this do?", category=Category.DEVELOPMENT)

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        for i in range(16):
            await message.channel.send(content=f"<@{message.author.id}>")
