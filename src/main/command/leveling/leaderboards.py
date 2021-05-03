import sqlite3

import discord

from command.command import Command, Parameter, Category


class Leaderboards(Command):
    def __init__(self):
        super().__init__("leaderboard", "Shows the levels leaderboard", ["leaderboards", "lb", "lboard"], [
            Parameter("page")], category=Category.LEVELING)

    # noinspection PyMethodParameters
    async def execute(self, message: discord.Message, parameters: str):
        try:
            offset = int(parameters)
        except:
            offset = 0

        sqlite_client = sqlite3.connect('bot_database.db')
        data_list = sqlite_client.execute('''SELECT ID, LEVEL, XP FROM LEVELS ORDER BY XP DESC LIMIT 3 OFFSET :offset''', {"offset": offset}).fetchall()

        print(data_list)
        for data in data_list:
            user = data[0]
            level = data[1]
            total_xp = data[2]

        message = await message.channel.send(data_list)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
