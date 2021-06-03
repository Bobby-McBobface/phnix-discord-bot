import asyncio

import levels
import discord
import configuration
import util
from enum import Enum
from commands import Category, CommandSyntaxError
# Registers all the commands; takes as a parameter the decorator factory to use.
def register_all(command):
    @command({
        "syntax": "test",
        "aliases": ["twoplustwo"],
        "role_requirements": {configuration.MODERATOR_ROLE},
        "category": Category.OTHER
    })
    async def test(message: discord.Message, parameters: str, client: discord.Client) -> None:
        """A command named 'test'"""
        result = 2 + 2
        await message.channel.send(f"Two plus two is {result}")

    @command({
        "syntax": "pad <message>",
        "category": Category.OTHER,
        "description": "Spaces out your text"
    })
    async def pad(message: discord.Message, parameters: str, client: discord.Client) -> None:
        """Spaces out your text"""
        if parameters == None:
            raise CommandSyntaxError
        else:
            await message.channel.send(" ".join(parameters))

    @command({
        "syntax": "hug <target>",
        "allowed_channels": [329226224759209985, 827880703844286475],
        "category": Category.OTHER,
        "description": "Hug someone"
    })
    async def hug(message: discord.Message, parameters: str, client: discord.Client) -> None:
        # Make sure someone was specified
        if parameters != None:
            parameters = parameters.strip()
        else:
            raise CommandSyntaxError("You must specify someone to hug.")
        # Get users
        hugger = message.author.mention
        target = parameters
        if hugger == target:
            #reply message should be a pun
            reply = util.choose_random(configuration.STRINGS_PUN).format(hugger=hugger)
        else:
            # Get a random message and fill it in
            choice = util.choose_random(configuration.STRINGS_HUG)
            reply = choice.format(hugger=hugger, target=target)
        # Make a fancy embed so people don't complain about getting pinged twice
        R, G, B = 256 * 256, 256, 1
        embed = discord.Embed(
            description=reply,
            colour=(46*R + 204*G + 113*B)
        )
        # Done
        await message.channel.send(embed=embed)
        if "<@!832151395989848084>" in target:
            await message.channel.send('Thanks for hugging me, I love that!')

    @command({
        "syntax": "replytome [text to echo]",
        "category": Category.OTHER,
        "description": "Replies to you"
    })
    async def replytome(message: discord.Message, parameters: str, client: discord.Client) -> None:
        if parameters == None:
            text = util.choose_random(("ok", "no"))
        else:
            text = parameters
            await message.channel.send(content=text, reference=message)

    @command({
        "syntax": "aa",
        "aliases": ["a"*a for a in range(1, 12)],
        "description": "AAAAAAAAAAAAAAAAAA",
        "category": Category.OTHER
    })
    async def aa(message: discord.Message, parameters: str, client: discord.Client) -> None:
        await message.channel.send(content="AAAAAAAAAAAAAAAAAAAAAAAA", reference=message)
