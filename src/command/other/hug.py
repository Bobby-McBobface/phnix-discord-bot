import discord

from command.command import Command, Category, Permission, CommandSyntaxError, Parameter
from config import config
import util


class Pad(Command):

    def __init__(self):
        super().__init__("hug", "Give a virtual hug to someone.", parameters=[Parameter("target", True)], category=Category.OTHER)

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        if not parameters:
            raise CommandSyntaxError("You must specify someone to hug.")
        else:
            # Get users
            hugger = message.author.mention
            target = parameters
            # Get a random message and fill it in
            choice = util.choose_random(config['messages']['stringsHug'])
            reply = choice.format(hugger=hugger, target=target)
            # Make a fancy embed so people don't complain about getting pinged twice
            R, G, B = 256 * 256, 256, 1
            embed = discord.Embed(
                description=reply,
                colour=(46 * R + 204 * G + 113 * B)
            )
            # Done
            await message.channel.send(embed=embed)
