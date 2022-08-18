"""Util functions for bot."""
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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if we should respond to the interaction.
        Defaults to if original invoker pressed the button.
        """
        should_respond = interaction.user.id == self.invoker_id
        if not should_respond:
            await interaction.response.defer(thinking=False)
        return should_respond

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
