import discord

from command.command import Command, Category, Permission
from config import config


class Ping(Command):

    def __init__(self):
        super().__init__("ping", "Checks the bot's response time.", ["pong"], category=Category.SYSTEM)

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        start_time = (message.id >> 22) + 1420070400000
        ping_message = await message.channel.send("Pong! :ping_pong:")
        end_time = (ping_message.id >> 22) + 1420070400000
        await ping_message.edit(content=f'Pong! Round trip: {end_time - start_time} ms', suppress=True)