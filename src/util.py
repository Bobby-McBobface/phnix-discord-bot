"""Util functions for bot."""

import asyncio
import re
from abc import ABC, abstractmethod
from typing import Any, Iterable, Sequence, TypedDict

import aiosqlite
import discord
from discord import ui
from discord.ext import commands


async def async_db_execute(sql: str, parameters: Iterable[Any] = ()) -> list[Any]:
    """Handles connections and execution of DB queries."""
    async with aiosqlite.connect(r"db.sqlite3") as conn:
        # Fetchall because cannot fetch when connection closed
        cur = await conn.execute_fetchall(sql, parameters)
        # Commiting doesn't do anything if nothing changed, convenient
        # Maybe in future use botvar and do bot.conn.commit() inside command
        await conn.commit()
        return cur  # type: ignore sqlite3.fetchall() actually returns list[Any]


class Paginator(ui.View, ABC):
    """
    Paginator with buttons.
        - Discord.py 2.1 has plans to update ext.menus to use buttons,
        - but until then, we'll use this
    """

    def __init__(
        self, invoker_id: int, page: int, page_total: int, *, timeout: float = 180
    ):
        super().__init__(timeout=timeout)
        if page_total < page:
            raise ValueError("Total pages more than current page")
        if page_total <= 0:
            raise ValueError("Total pages less than 1")
        if page_total == 1:  # No need for pagination
            self.clear_items()
        if page == 1:
            self._backward.disabled = True
        elif page == page_total:
            self._foward.disabled = True

        self.invoker_id = invoker_id
        self.page = page
        self.page_total = page_total
        self._page_display.label = f"{self.page}/{self.page_total}"

    async def disable_buttons(self) -> None:
        """Disable all active buttons in view."""
        for child in self.children:
            if isinstance(child, ui.Button):
                child.disabled = True

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        """
        Checks if we should respond to the interaction.
        Defaults to if original invoker pressed the button.
        """
        same_author = interaction.user.id == self.invoker_id
        if not same_author:
            paginator_copy = self.__class__(
                interaction.user.id,
                self.page,
                self.page_total,
                timeout=self.timeout or 180,
            )
            asyncio.create_task(paginator_copy.wait())
            await interaction.response.send_message(
                **await paginator_copy.get_content(interaction),  # type: ignore
                view=paginator_copy,
                ephemeral=True,
            )
        return same_author

    class GetContentReturnType(TypedDict, total=False):
        """What Paginator.get_content should return."""

        content: str | None
        embed: discord.Embed | None
        embeds: Sequence[discord.Embed]
        attachments: Sequence[discord.Attachment | discord.File]

    @abstractmethod
    async def get_content(
        self, ctx: discord.Interaction | commands.Context
    ) -> GetContentReturnType:
        """Return content based on page"""
        blank: Paginator.GetContentReturnType = {
            "content": "...",
        }
        return blank

    async def _on_page_change(self, interaction: discord.Interaction):
        await self._update_page_display()
        new_content = await self.get_content(interaction)
        content = new_content.get("content", None)
        embed = new_content.get("embed", None)
        attachments = new_content.get("attachments", [])

        if embed is None:
            embeds = new_content.get("embeds", [])
        else:
            embeds = [embed]

        await interaction.response.edit_message(
            content=content,
            embeds=embeds,
            attachments=attachments,
            view=self,
        )

    async def _update_page_display(self):
        self._page_display.label = f"{self.page:,}/{self.page_total:,}"

    @ui.button(label="<")
    async def _backward(self, interaction: discord.Interaction, button: ui.Button):
        self.page -= 1
        if self.page == 1:
            button.disabled = True
        self._foward.disabled = False

        await self._on_page_change(interaction)

    @ui.button(label="N/A", disabled=True)
    async def _page_display(self, *_):
        """Button to display current page total pages of the paginator"""

    @ui.button(label=">")
    async def _foward(self, interaction: discord.Interaction, button: ui.Button):
        self.page += 1
        if self.page == self.page_total:
            button.disabled = True
        self._backward.disabled = False
        await self._on_page_change(interaction)


# Copyright (c) 2022 Vercel, Inc.
# https://github.com/vercel/ms


# pylint: disable=line-too-long, too-many-return-statements
def parse_timeframe_ms(string) -> float | None:
    """Converts human readable timeframes to milliseconds"""
    if len(string > 100):
        raise ValueError("Value exceeds the maximum length of 100 characters.")

    match = re.match(
        r"^(?P<value>-?(?:\d+)?\.?\d+) *(?P<type>milliseconds?|msecs?|ms|seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|w|years?|yrs?|y)?$",
        string,
    )

    if not match:
        return None

    value = float(match.group("value"))
    multiplier_type = match.group("type").lower() or "ms"

    match multiplier_type:
        case "years" | "year" | "yrs" | "yr" | "y":
            return value * 1000 * 60 * 60 * 24 * 365.25
        case "weeks" | "week" | "w":
            return value * 1000 * 60 * 60 * 24 * 7
        case "days" | "day" | "d":
            return value * 1000 * 60 * 60 * 24
        case "hours" | "hour" | "hrs" | "hr" | "h":
            return value * 1000 * 60 * 60
        case "minutes" | "minute" | "mins" | "min" | "m":
            return value * 1000 * 60
        case "seconds" | "second" | "secs" | "sec" | "s":
            return value * 1000
        case "milliseconds" | "millisecond" | "msecs" | "msec" | "ms":
            return value
        case _:
            # This should never occur.
            raise ValueError(
                f"The unit {multiplier_type} was matched, but no matching case exists."
            )
