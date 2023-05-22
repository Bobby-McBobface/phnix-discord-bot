import asyncio
import traceback
from json import loads

import discord
from urllib3 import PoolManager

import configuration

http = PoolManager()


async def twitch(client: discord.Client) -> None:
    """
    Gets a list of new twich videos from an RSS feed and posts them to a
    configured subreddit.
    As this is designed for Phoenix SC's channel, this assumes all livestreams
    include the text ``LIVE //`` in the video title.
    Arguments:
        sub (str): The subreddit name (without the r/) that you wish to
            post new videos to.
        reddit (praw.Reddit): The Reddit connection to use to process the check
        debug (bool): Used for testing purposes. Currently does nothing.
    """
    with open("last_stream.ini", "a+"):
        # create file
        pass

    # Get RSS feeds #
    while True:
        try:
            await get_stream(client)
            await asyncio.sleep(configuration.TWITCH_SLEEP)
        except Exception as e:
            print("Twitch error:", e)
            traceback.print_exc()
            await asyncio.sleep(configuration.TWITCH_SLEEP)


async def refresh_token() -> None:
    with open("env/twitch_client_id") as file:
        client_id = file.read()

    with open("env/twitch_secret") as file:
        secret = file.read()

    r = http.request(
        "POST",
        f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={secret}&grant_type=client_credentials")

    data = loads(r.data.decode('utf-8'))

    with open("env/twitch_auth_token", "w") as file:
        file.write(data["access_token"])


async def get_stream(client: discord.Client) -> None:
    """
    Args:
    client: discord.Client
    """

    with open("env/twitch_client_id") as file:
        client_id = file.read()

    with open("env/twitch_auth_token") as file:
        auth_token = file.read()

    r = http.request("GET", f"https://api.twitch.tv/helix/streams?user_id={configuration.TWITCH_CHANNEL_ID}",
                     headers={'client-id': client_id, 'Authorization': f'Bearer {auth_token}'})

    if r.status == 401:
        await refresh_token()
        return

    data = loads(r.data.decode('utf-8'))["data"]

    if data:
        stream_id = data[0]["id"]

        with open("last_stream.ini", "r+") as file:
            if file.read() != stream_id:
                # New stream
                file.seek(0)
                file.truncate(0)
                file.write(data[0]["id"])
                await post_stream(client)


async def post_stream(client: discord.Client) -> None:
    title = "Phoenix has started a new stream"
    guild = client.get_guild(configuration.GUILD_ID)
    channel = guild.get_channel(configuration.FEED_CHANNEL)

    await channel.send(f"Hey <@&{configuration.TWITCH_PING}>, {title} at https://twitch.tv/PhoenixSCLive !",
                       allowed_mentions=discord.AllowedMentions(roles=True))
