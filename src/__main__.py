import os

from discord import Intents
from discord import AllowedMentions
from discord.ext.commands import Bot
from discord_slash import SlashCommand

from dotenv import load_dotenv

import configuration
from cogs.misc import Misc
from cogs.level import Leveling

if __name__ == "__main__":
    load_dotenv()

    intents = Intents.none()
    intents.guilds = True
    intents.members = True
    intents.guild_messages = True
    intents.guild_reactions = True

    allowed_mentions = AllowedMentions(
        everyone=False,
        roles=False,
        users=True,
        replied_user=True
    )

    client = Bot(
        configuration.PREFIX,
        case_insensitive=True,
        strip_after_prefix=True,
        intents=intents, 
        allowed_mentions=allowed_mentions,
        description="phex bot",  
    )

    slash = SlashCommand(client, sync_commands=True)

    client.add_cog(Misc())

    client.run(os.environ["TOKEN"])
