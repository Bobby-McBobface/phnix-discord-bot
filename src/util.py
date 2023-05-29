import asyncio
from random import choice
from typing import Callable

import discord

import configuration


def get_member_by_id_or_name(message, user: str) -> discord.Member or None:
    if user == "":
        return None

    member = None
    try:
        member = message.guild.get_member(int(user.strip('<@!>')))
    except ValueError:
        pass

    if member == None:
        member = message.guild.get_member_named(user)

    return member


async def split_into_member_and_reason(message: discord.Message, parameters: str) -> tuple:
    """
    Splits parameters into member and reason.
    Used for most moderation commands.
    """

    if parameters == "":
        return None, None

    split_params = parameters.split(maxsplit=1)
    member = get_member_by_id_or_name(message, split_params[0])
    try:
        reason = split_params[1].lstrip('| ')
    except IndexError:
        reason = None

    if member == None:
        # Reversed to split the last | in case someone has | in their name
        split_params_pipe = parameters[::-1].split("|", 1)

        member = get_member_by_id_or_name(message,
                                          split_params_pipe[len(split_params_pipe) - 1][::-1].rstrip())

        if len(split_params_pipe) == 2:
            # Unreverse
            reason = split_params_pipe[0][::-1].lstrip()
        else:
            reason = None

    return member, reason


def try_get_valid_user_id(id: str) -> int:
    try:
        user_id = id.strip("<@!>")
        user_id = int(user_id)
    except ValueError:
        return 0
    if len(str(user_id)) not in range(17, 20):
        return 0

    return user_id


def choose_random(choices: list):
    """Returns a random item from `choices`"""
    return choice(choices)


def check_if_string_invisible(string: str) -> bool:
    """Returns True if the string is comprised entirely of non-visible characters."""
    for char in string:
        if char not in configuration.INVISIBLE_CHARACTERS:
            # String must be visible if this is the case
            return False
    # If the for loop ended, then every character must be invisible.
    return True


def check_mod_or_test_server(message: discord.Message) -> bool:
    if message.guild.get_role(configuration.MODERATOR_ROLE) in message.author.roles \
            or message.guild.id != configuration.GUILD_ID:
        return True
    return False


def is_valid_duration(duration: str, scale: int) -> int or None:
    try:
        return int(duration) * scale
    except:
        return None


def is_hex(c) -> bool:
    try:
        n = int(c, 16)
        return True
    except ValueError:
        return False


def RGB_to_hex(RGB):
    """ [255,255,255] -> "#FFFFFF" """
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#" + "".join(["0{0:x}".format(v) if v < 16 else
                          "{0:x}".format(v) for v in RGB])


def convert_hex_to_rgb(hex: str) -> list:
    hex = str(hex).lstrip("#")
    rgb = list(int(hex[i:i + 2], 16) for i in (0, 2, 4))
    return rgb


def color_dict(gradient):
    """ Authored by https://bsouthga.dev/posts/color-gradients-with-python;
      Takes in a list of RGB sub-lists and returns dictionary of colors in RGB and hex form
      or use in a graphing function defined later on """

    return {"hex": [RGB_to_hex(RGB) for RGB in gradient],
            "r": [RGB[0] for RGB in gradient],
            "g": [RGB[1] for RGB in gradient],
            "b": [RGB[2] for RGB in gradient]}


def linear_gradient(start_hex, finish_hex="#FFFFFF", samples=10):
    """ Authored by https://bsouthga.dev/posts/color-gradients-with-python;
        returns a gradient list of (n) colors between two hex colors. start_hex and finish_hex
        should be the full six-digit color string, inlcuding the number sign ("#FFFFFF") """

    # Starting and ending colors in RGB form
    s = convert_hex_to_rgb(start_hex)
    f = convert_hex_to_rgb(finish_hex)

    # Initilize a list of the output colors with the starting color
    RGB_list = [s]

    # Calcuate a color at each evenly spaced value of t from 1 to samples
    if samples <= 1:
        samples = 2

    for t in range(1, samples):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [int(s[j] + (float(t) / (samples - 1)) * (f[j] - s[j])) for j in range(3)]

        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return color_dict(RGB_list)


class ReactionPageHandle:
    def __init__(self, client: discord.Client, message: discord.Message, op: discord.Member,
                 data_source: Callable[[int, int], discord.Embed], page: int, total_pages: int):

        self.client = client
        self.message = message
        self.op = op
        self.data_source = data_source
        self.page = page
        self.total_pages = total_pages

    async def start(self):
        await self.message.add_reaction("◀️")
        await self.message.add_reaction("▶️")

        await self.page_change()

    def check(self, reaction: discord.Reaction, user: discord.Member):
        if self.op.id != user.id or reaction.message.id != self.message.id:
            return False

        emoji = reaction.emoji

        if emoji not in ["◀️", "▶️"]:
            return False

        asyncio.get_running_loop().create_task(reaction.remove(user))

        if emoji == "◀️" and self.page > 0:
            self.page += -1
        elif emoji == "▶️" and self.page < self.total_pages:
            self.page += 1
        else:
            return False
        return True

    async def page_change(self):
        new_page_embed = self.data_source(self.page, self.total_pages)
        await self.message.edit(embed=new_page_embed)
        try:
            await self.client.wait_for('reaction_add', timeout=30.0, check=self.check)
            await self.page_change()
        except asyncio.TimeoutError:
            await self.message.clear_reactions()
