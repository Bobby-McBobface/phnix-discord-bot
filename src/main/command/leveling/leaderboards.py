import asyncio
import sqlite3

import discord

from command.command import Command, Parameter, Category


class Leaderboards(Command):
    def __init__(self):
        super().__init__("leaderboard", "Shows the levels leaderboard", ["leaderboards", "lb", "lboard"], [
            Parameter("page")], category=Category.LEVELING)

    async def change_page(self, message: discord.Message, page: int, client: discord.Client):
        sqlite_client = sqlite3.connect('bot_database.db')
        data_list = sqlite_client.execute('''SELECT ID, LEVEL, XP FROM LEVELS ORDER BY XP DESC LIMIT 3 OFFSET :offset''', {"offset": page}).fetchall()

        lb_list = ''
        for data in data_list:
            user = data[0]
            level = data[1]
            total_xp = data[2]
            lb_list += f"<@{user}> | Level: {level} | Total XP: {total_xp}\n"

        embed = discord.Embed(title="Leaderboard", description=lb_list)

        msg = await message.edit(embed=embed)
        await self.leaderboard_pages(msg, page, client)

    async def leaderboard_pages(self, message: discord.Message, page: int, client: discord.Client):
        change_to = ''

        def check(reaction, user):
            if user.bot:
                return False

            valid = str(reaction.emoji) == "◀️" or str(reaction.emoji) == "▶️"
            if not valid:
                return False

            emoji = reaction.emoji
            asyncio.get_running_loop().create_task(reaction.remove(user))
            if emoji == "◀️" and page > 0:
                self.change_to = 'previous'
            elif emoji == "▶️":
                self.change_to = 'next'
            return valid

        await client.wait_for('reaction_add', timeout=60.0, check=check)
        if change_to == 'next':
            await self.change_page(message, page + 1, client)
        elif change_to == 'previous':
            await self.change_page(message, page - 1, client)

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        try:
            offset = int(parameters)
        except:
            offset = 0
        sqlite_client = sqlite3.connect('bot_database.db')
        data_list = sqlite_client.execute('''SELECT ID, LEVEL, XP FROM LEVELS ORDER BY XP DESC LIMIT 3 OFFSET :offset''', {"offset": offset}).fetchall()

        lb_list = ''
        for data in data_list:
            user = data[0]
            level = data[1]
            total_xp = data[2]
            lb_list += f"<@{user}> | Level: {level} | Total XP: {total_xp}\n"

        embed = discord.Embed(title="Leaderboard", description=lb_list)

        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("◀️")
        await msg.add_reaction("▶️")
        await self.leaderboard_pages(msg, offset, client)
