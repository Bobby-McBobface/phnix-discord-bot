import asyncio
from json import loads

import discord
import dotenv
from urllib3 import PoolManager

import main

http = PoolManager()


async def twitch(client):
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

    # Get RSS feeds #
    while True:
        await get_stream(client)
        await asyncio.sleep(main.config['twitchSleep'])


async def refresh_token():
    client_id = dotenv.get_key(".env", "TWITCH_CLIENT_ID")
    secret = dotenv.get_key(".env", "TWITCH_SECRET")

    r = http.request("POST",
                     f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={secret}&grant_type=client_credentials")

    data = loads(r.data.decode('utf-8'))

    print(data["access_token"])

    dotenv.set_key(".env", "TWITCH_AUTH_TOKEN", data["access_token"], "never")


async def get_stream(client):
    '''
    Args:
    client: discord.Client
    '''

    client_id = dotenv.get_key(".env", "TWITCH_CLIENT_ID")
    auth_token = dotenv.get_key(".env", "TWITCH_AUTH_TOKEN")

    r = http.request("GET", f"https://api.twitch.tv/helix/streams?user_id={main.config['twitchChannelId']}",
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


async def post_stream(client):
    title = "Phoenix has started a new stream"
    guild = client.get_guild(main.config['guildId'])
    channel = guild.get_channel(main.config['feedChannel'])

    await channel.send(f"Hey <@&{main.config['twitchPing']}>, {title} at https://twitch.tv/PhoenixSCLive !",
                       allowed_mentions=discord.AllowedMentions(roles=True))
