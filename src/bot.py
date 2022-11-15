"""Main code to set up and run the bot."""
import os
import traceback

import aiohttp
import discord
import dotenv
from discord.ext import commands

from cogs.levels import Levels
from cogs.misc import Miscellaneous
from cogs.moderation import Moderation
from cogs.starboard import Starboard

# from cogs.youtube_twitch import YouTubeTwitch
from constants import ALLOWED_GUILD_IDS

try:
    import uvloop  # type: ignore
except ImportError:
    pass


class MyBot(commands.Bot):
    """My bot."""

    def __init__(self) -> None:
        intents = discord.Intents.none()
        # pylint: disable=assigning-non-slot
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.guild_reactions = True
        # pylint: enable=assigning-non-slot
        super().__init__(
            commands.when_mentioned_or("!"),
            case_insensitive=True,
            strip_after_prefix=True,
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
        )

    async def setup_hook(self):
        # self.loop.set_debug(True)
        # async with aiosqlite.connect(r"db.sqlite3") as conn:
        #     with open(r"db.schema", encoding="utf-8") as file:
        #         await conn.executescript(file.read())

        await self.add_cog(Levels(self))
        await self.add_cog(Moderation())
        await self.add_cog(Miscellaneous())
        await self.add_cog(Starboard(self))
        # await self.add_cog(YouTubeTwitch())

    async def on_command_error(self, context, exception, /) -> None:
        if isinstance(exception, commands.CommandNotFound):
            return
        if isinstance(
            exception,
            (
                commands.CheckFailure,
                commands.UserInputError,
                commands.CommandOnCooldown,
            ),
        ):
            await context.reply(str(exception))
            return

        await context.reply("An unknown error occured")
        raise exception  # Will get handled in self.on_error

    async def on_error(self, event_method: str, /, *args, **kwargs) -> None:
        await super().on_error(event_method, *args, **kwargs)
        err_webhook_url = os.environ.get("ERROR_WEBHOOK")
        if not err_webhook_url:
            return
        async with aiohttp.ClientSession() as session:
            try:
                err_webhook = discord.Webhook.from_url(err_webhook_url, session=session)
                await err_webhook.send(content=traceback.format_exc())
            except discord.HTTPException:
                print(f"Error sending error to webhook: {traceback.format_exc()}")


def main():
    """Runs the bot."""
    try:
        uvloop.install()
    except NameError:  # only on linux
        pass

    dotenv.load_dotenv()
    bot = MyBot()

    @bot.check
    async def _restrict_servers(ctx: commands.Context):
        return ctx.guild.id in ALLOWED_GUILD_IDS if ctx.guild else False

    bot.run(os.environ["TOKEN"])


if __name__ == "__main__":
    main()
