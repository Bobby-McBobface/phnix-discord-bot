# copied from reddit bot
import asyncio
import traceback
from datetime import datetime

import discord
from feedparser import parse

import configuration

main_channel = "UCj4zC1Hfj-uc90FUXzRamNw"
sucks_at = "UC9T9mnA5u12DlQjeywuonpw"


async def youtube(client: discord.Client) -> None:
    """
    Gets a list of new YouTube videos from an RSS feed and posts them to a
    configured subreddit.
    As this is designed for Phoenix SC's channel, this assumes all livestreams
    include the text ``LIVE //`` in the video title.
    Arguments:
        sub (str): The subreddit name (without the r/) that you wish to
            post new videos to.
        reddit (praw.Reddit): The Reddit connection to use to process the check
        debug (bool): Used for testing purposes. Currently does nothing.
    """
    # Create files if they don't exist
    try:
        with open(f"last_video_{main_channel}.ini", "r") as file:
            pass
    except FileNotFoundError:
        with open(f"last_video_{main_channel}.ini", "w") as file:
            file.write(str(datetime.now()))

    try:
        with open(f"last_video_{sucks_at}.ini", "r") as file:
            pass
    except FileNotFoundError:
        with open(f"last_video_{sucks_at}.ini", "w") as file:
            file.write(str(datetime.now()))

    # Get RSS feeds #
    while True:
        try:
            await handle_feed(main_channel, client)
            await handle_feed(sucks_at, client)
            await asyncio.sleep(configuration.YOUTUBE_SLEEP)
        except Exception as e:
            print("Youtube error:", e)
            traceback.print_exc()
            await asyncio.sleep(configuration.YOUTUBE_SLEEP)


async def handle_feed(channel_id: str, client: discord.Client) -> None:
    # Check if updated #
    last_entry = open('last_video_' + channel_id + '.ini', 'r')

    feed_base_url = 'https://www.youtube.com/feeds/videos.xml?channel_id='
    yt_feed = parse(feed_base_url + channel_id)

    # This is commented out for archival purposes. #
    # if yt_feed == []: #Stops crash due to list index out of range
    #     return

    # Split feed elements #
    try:  # Catches case where there is an error in parsing the feed and it returns an unexpected object
        entry = yt_feed.entries[0]
    except IndexError:
        return
    title = entry.title
    date = datetime.strptime(
        entry.published[:16], "%Y-%m-%dT%H:%M")  # 2020-05-20T01:00
    url = entry.link
    channel = entry.author

    # Duplication detection via date checking#
    last_date = last_entry.readline()

    last_date = datetime.strptime(last_date[:16], "%Y-%m-%d %H:%M")

    # Checks to see that it isn't a livestream
    if date > last_date and title.find('LIVE //') == -1:
        updated = True

    else:
        updated = False
    last_entry.close()

    # Update if updated #

    if updated:
        # yt_post_flair = config['yt_post_flair']

        # calls function to post video
        await postvid(title, url, channel, client)

        last_date = date
        # updates the latest date in the function
        last_entry = open('last_video_' + channel_id + '.ini', 'w')
        last_entry.write(str(date))

        last_entry.close()


async def postvid(title: str, url: str, channel: str,
                  client: discord.Client) -> None:  # function that handles video posts
    """
    Posts the video to Reddit with the specified configuration parameters.
    Arguments:
        title (str): The title of the video to be posted.
        url (str): The URL of the video to be posted.
        sub (str): The subreddit name (without the r/) that you wish to
            post new videos to.
        reddit (praw.Reddit): The Reddit connection to use to process the check
        debug (bool): Used for testing purposes. Currently does nothing.
    """

    title = ("Phoenix has posted a new video: " + title)
    guild = client.get_guild(configuration.GUILD_ID)
    channel = guild.get_channel(configuration.FEED_CHANNEL)

    await channel.send(f"Hey <@&{configuration.YOUTUBE_PING}>, {title} at {url}!",
                       allowed_mentions=discord.AllowedMentions(roles=True))
