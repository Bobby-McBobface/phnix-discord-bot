"""Cog to handle feeds from YouTube and Twitch."""
import asyncio
import hashlib
import hmac
import json
import os
from xml.etree import ElementTree as ET

import aiohttp
from aiohttp import web
from discord.ext import commands


class YouTubeTwitch(commands.Cog):
    """Starts a webserver to post new Twitch streams and YouTube videos to Discord."""

    FEED_WEBHOOK_URL = ""

    def __init__(self) -> None:
        self.FEED_WEBHOOK_URL = os.environ.get(
            "FEED_WEBHOOK"
        )  # pylint: disable=invalid-name
        if not self.FEED_WEBHOOK_URL:
            raise ValueError("Feed webhook not provided")
        if not os.environ.get("TWITCH_HMAC"):
            raise ValueError("Missing Twitch HMAC key")
        if not os.environ.get("YOUTUBE_HMAC"):
            raise ValueError("Missing YouTube HMAC key")

        app = web.Application()
        app.add_routes(
            [
                web.post("/yt", self.youtube_post),
                web.get("/yt", self.youtube_get),
                web.post("/twitch", self.twitch),
            ]
        )
        self.runner = web.AppRunner(app)
        self.yt_pending_challenge = False

    async def cog_load(self) -> None:
        await self.runner.setup()
        site = web.TCPSite(self.runner, "::", 8080)
        await site.start()
        # await refresh_yt_subscription()

    async def cog_unload(self) -> None:
        await self.runner.cleanup()

    async def _refresh_yt_subscription(self, seconds: int):
        await asyncio.sleep(seconds)
        await self.refresh_yt_subscription()

    async def refresh_yt_subscription(self):
        """Refreshes PubSubHubBub subscription"""
        return
        # async with aiohttp.ClientSession() as session:
        #     self.yt_pending_challenge = True
        #     await session.post(
        #         "https://pubsubhubbub.appspot.com/subscribe",
        #         params={
        #             "hub.callback": os.environ.get("SERVER_HOSTNAME"),
        #             "hub.topic": "a",
        #             "hub.verify": "sync",
        #             "hub.mode": "subscribe",
        #             "hub.secret": os.environ.get("YOUTUBE_HMAC", "KEY"),
        #             "hub.lease_seconds": 10 * 24 * 60 * 60,  # 10 days
        #         },
        #     )
        #     self.yt_pending_challenge = False

    async def youtube_get(self, request: web.Request):
        """YouTube PubSubbHubBub subscription handler"""
        challenge = request.query.get("hub.challenge")
        if challenge:
            # TODO: put in database and resubscribe pylint: disable=fixme
            # I can't be bothered to fix this, fix later
            # Just get a cron job to do it idk
            # lease_seconds = int(request.query.get("hub.lease_seconds", 60))
            # Refresh 30 seconds before lease expires
            # asyncio.create_task(self._refresh_yt_subscription(lease_seconds - 30))
            return web.Response(text=challenge)
        return web.Response(status=400)

    async def youtube_post(self, request: web.Request):
        """YouTube post route handler"""
        hmac_header = request.headers.get("X-Hub-Signature", None)
        content = await request.content.read()
        if not hmac_header:
            return web.Response(status=204)
        digest = hmac.new(
            bytes(os.environ.get("YOUTUBE_HMAC", ""), "utf-8"), content, hashlib.sha1
        )
        if not hmac.compare_digest(digest.hexdigest(), hmac_header[5:]):
            return web.Response(status=204)

        # Process data
        print("Recieved video")
        data = ET.fromstring(content)

        asyncio.create_task(self.post_yt_vid(data))
        return web.Response(status=204)

    async def post_yt_vid(self, xml: ET.Element):
        """Posts the video to Discord"""
        if (
            (tmp := xml.find("{http://www.w3.org/2005/Atom}entry"))
            and (tmp := tmp.find("{http://www.w3.org/2005/Atom}title"))
            and (title := tmp.text)
        ):  # PEP 505 when?
            data = {
                "content": (
                    f"Phoenix has just posted a video, but Modertron's slow: {title}"
                )
            }
        else:
            print("xml failed", xml)
            data = {"content": "Phoenix has just posted a video, but Modertron is slow"}

        async with aiohttp.ClientSession() as session:
            assert self.FEED_WEBHOOK_URL
            await session.post(self.FEED_WEBHOOK_URL, data=data)

    # ------------------------------------------------------------------------------- #

    async def twitch(self, request: web.Request):
        """Twitch route handler"""
        content = await request.content.read()
        body = (
            request.headers.get("Twitch-Eventsub-Message-Id", "")
            + request.headers.get("Twitch-Eventsub-Message-Timestamp", "")
            + str(content)[2:-1]  # remove b' and ending '
        )

        digest = hmac.new(
            bytes(os.environ.get("TWITCH_HMAC", ""), "utf-8"),
            bytes(body, "utf-8"),
            hashlib.sha256,
        )
        if not hmac.compare_digest(
            digest.hexdigest(),
            request.headers.get("Twitch-Eventsub-Message-Signature", "")[7:],  # sha256=
        ):
            return web.Response(status=403)

        notification = json.loads(content)
        request_type = request.headers.get("Twitch-Eventsub-Message-Type", None)

        if request_type == "notification":
            asyncio.create_task(self.post_twitch_stream())
            return web.Response(status=204)
        if request_type == "webhook_callback_verification":
            return web.Response(body=notification.get("challenge"))
        if request_type == "revocation":
            print("Twitch revoked")
            return web.Response(status=204)
        return web.Response(status=204)

    async def post_twitch_stream(self):
        """Posts Twitch stream url to Discord."""
        async with aiohttp.ClientSession() as session:
            assert self.FEED_WEBHOOK_URL
            await session.post(
                self.FEED_WEBHOOK_URL,
                data={
                    "content": "Phoenix just started a stream, but Modertron is slow."
                },
            )
