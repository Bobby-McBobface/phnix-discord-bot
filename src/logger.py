from typing import Union
import discord
import configuration


async def log_misc(source: str, content: str, client: discord.Client) -> None:
    embed_msg = discord.Embed(description=content)
    await send_logs(source, client, embed_msg)
    

async def log_moderation(message: discord.Message, warn_embed: discord.Embed, client: discord.Client) -> None:
    moderator = message.author.mention
    await send_logs(f"Moderator: {moderator}", client, warn_embed)


async def log_error(error: str, client: discord.Client) -> None:
    error_embed = discord.Embed(title="Error", description=error)
    await send_logs("", client, error_embed)


async def send_logs(message: str, client: discord.Client, embed: Union[discord.Embed, None]) -> None:
    try:
        await client.get_guild(configuration.GUILD_ID).get_channel(configuration.LOG_CHANNEL).send(message, embed=embed, allowed_mentions=discord.AllowedMentions(users=False))
    except Exception as e:
        print("Error sending logs:", e)
