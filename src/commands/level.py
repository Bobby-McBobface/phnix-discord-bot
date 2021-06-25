import asyncio
from commands import Category, CommandSyntaxError, command

import levels
import discord
import util
import database_handle
import configuration

# Registers all the commands; takes as a parameter the decorator factory to use.


@command({
    "syntax": "rank [user]",
    "aliases": ["wank", "level"],
    "category": Category.LEVELING,
    "description": "Check how much XP you have"
})
async def rank(message: discord.Message, parameters: str, client: discord.Client) -> None:
    if parameters != "":
        member = util.get_member_by_id_or_name(message, parameters)
        if member is None:
            raise CommandSyntaxError('You must specify a valid user.')
    else:
        member = message.author

    user_xp = database_handle.cursor.execute('''SELECT XP, LEVEL FROM LEVELS WHERE ID=:user_id''',
                                             {'user_id': member.id}).fetchone()
    if user_xp is None:
        await message.channel.send("The user isn't ranked yet.")
        return

    user_rank = database_handle.cursor.execute('''SELECT COUNT(*)+1 FROM LEVELS WHERE XP > :user_xp''',
                                               {'user_xp': user_xp[0]}).fetchone()

    avatar = member.avatar_url_as(format=None, static_format='png', size=1024)

    ranks = dict(filter(lambda elem: user_xp[1] < elem[1][1], configuration.LEVEL_ROLES.items()))
    if len(ranks) > 0:
        rank = list(ranks.items())[-1][1]
        next_rank = f"<@&{rank[0]}> | Level: {str(rank[1])}"
    else:
        next_rank = "Maximum rank reached."

    rank_embed = discord.Embed(description=f"Rank for <@{member.id}>") \
        .add_field(name="Total XP:", value=user_xp[0]) \
        .add_field(name="Level:", value=(user_xp[1])) \
        .add_field(name="Rank:", value="#" + str(user_rank[0])) \
        .add_field(name="XP until level up:", value=levels.xp_needed_for_level(user_xp[1] + 1) - user_xp[0]) \
        .add_field(name="Next rank:", value=next_rank) \
        .set_author(name=f"{member.name}#{member.discriminator}", icon_url=avatar.__str__())

    await message.channel.send(embed=rank_embed)


@command({
    "syntax": "leaderboards [page number]",
    "aliases": ["lb", "levels"],
    "category": Category.LEVELING,
    "description": "Shows a list of all users and their XP"
})
async def leaderboards(message: discord.Message, parameters: str, client: discord.Client, first_execution=True, op=None, page_cache=0) -> None:
    try:
        page = int(parameters)
    except:
        # Human friendly compensation
        page = 0

    if first_execution:
        response = await message.channel.send(embed=discord.Embed(title="Loading"))
        await response.add_reaction("◀️")
        await response.add_reaction("▶️")

        total_pages = database_handle.cursor.execute(
            '''SELECT COUNT(*) FROM LEVELS''').fetchone()[0] // 10

        await leaderboards(response, page, client, first_execution=False, op=message.author.id, page_cache=total_pages)
        return

    data_list = database_handle.cursor.execute('''SELECT ID, LEVEL, XP FROM LEVELS ORDER BY XP DESC LIMIT 10 OFFSET :offset''',
                                               {"offset": page * 10}).fetchall()

    lb_list = ''.join(
        f"{page * 10 + index + 1}: <@{data[0]}> | Level: {data[1]} | Total XP: {data[2]}\n" for index, data in enumerate(data_list))

    if not lb_list:
        lb_list = "No data on this page!"

    embed = discord.Embed(title="Leaderboard", description=lb_list).set_footer(
        text=f"Page: {page + 1}/{page_cache + 1}")
    await message.edit(embed=embed)

    def check(reaction, user):
        if op != user.id:
            return False

        if reaction.message.id != message.id:
            return False

        emoji = reaction.emoji

        valid = emoji == "◀️" or emoji == "▶️"
        if not valid:
            return False
        asyncio.get_running_loop().create_task(reaction.remove(user))
        nonlocal page
        if emoji == "◀️" and page > 0:
            page += -1
        elif emoji == "▶️" and page < page_cache:
            page += 1
        else:
            return False
        return True

    try:
        await client.wait_for('reaction_add', timeout=30.0, check=check)
        await leaderboards(message, page, client, first_execution=False, op=op, page_cache=page_cache)
    except asyncio.TimeoutError:
        await message.clear_reactions()
