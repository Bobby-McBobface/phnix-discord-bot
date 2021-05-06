import asyncio
import sqlite3

import discord

from command.command import Command, Parameter, Category


class Leaderboards(Command):
    def __init__(self):
        super().__init__("leaderboard", "Shows the levels leaderboard", ["leaderboards", "lb", "lboard"], [
            Parameter("page")], category=Category.LEVELING)

    async def change_page(self):
        sqlite_client = sqlite3.connect('data/bot_database.db')
        data_list = sqlite_client.execute('''SELECT ID, LEVEL, XP FROM LEVELS ORDER BY XP DESC LIMIT 3 OFFSET :offset''', {"offset": self.page}).fetchall()

        lb_list = ''
        for data in data_list:
            user = data[0]
            level = data[1]
            total_xp = data[2]
            lb_list += f"<@{user}> | Level: {level} | Total XP: {total_xp}\n"

        embed = discord.Embed(title="Leaderboard", description=lb_list)

        await self.response.edit(embed=embed)
        await self.wait_for_reaction()

    async def wait_for_reaction(self):
        def check(reaction, user):
            if self.op != user.id:
                return False

            if reaction.message.id != self.response.id:
                return False

            emoji = reaction.emoji
            
            valid = emoji == "◀️" or emoji == "▶️"
            if not valid:
                return False
            asyncio.get_running_loop().create_task(reaction.remove(user))
            if emoji == "◀️" and self.page > 0:
                self.page += -1
            elif emoji == "▶️":
                self.page += 1
            return True

        try:
            await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            await self.change_page()
        except asyncio.TimeoutError:
            await self.response.clear_reactions()

    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        try:
            self.page = int(parameters)
        except:
            self.page = 0

        embed = discord.Embed(title="Leaderboard", description="Loading")
        self.op = message.author.id
        self.client = client

        self.response = await message.channel.send(embed=embed)
        await self.response.add_reaction("◀️")
        await self.response.add_reaction("▶️")
        await self.change_page()

