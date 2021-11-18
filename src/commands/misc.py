import discord
import configuration
import util
from commands import Category, CommandSyntaxError, command

# Registers all the commands; takes as a parameter the decorator factory to use.
@command({
    "syntax": "test",
    "aliases": ["twoplustwo"],
    "role_requirements": {configuration.MODERATOR_ROLE},
    "category": Category.OTHER
})
async def test(message: discord.Message, parameters: str, client: discord.Client) -> None:
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")

@command({
    "syntax": "pad <message>",
    "category": Category.OTHER,
    "description": "Spaces out your text"
})
async def pad(message: discord.Message, parameters: str, client: discord.Client) -> None:
    """Spaces out your text"""
    if parameters == "":
        raise CommandSyntaxError("You must specify text to space out.")
    elif len(parameters) > 1000:
        await message.channel.send("Message must not surpass 1000 characters")
    else:
        await message.channel.send(" ".join(parameters))

@command({
    "syntax": "hug <target>",
    "allowed_channels": [329226224759209985, 827880703844286475],
    "category": Category.OTHER,
    "description": "Hug someone"
})
async def hug(message: discord.Message, parameters: str, client: discord.Client) -> None:
# Make sure someone was specified
    if parameters == "":
        raise CommandSyntaxError("You must specify someone to hug.")
    # Get users
    hugger = message.author.mention
    target = parameters
    
    if str(message.author.id) in target:
        #reply message should be a pun
        reply = util.choose_random(configuration.STRINGS_PUN).format(hugger=hugger)
    else:
        
        if target.lower() == "me":
            await message.channel.send("Aw, do you need a hug?")
            # Make Modertron hug the user instead
            target = hugger
            hugger = client.user.mention
        
        # Get a random message and fill it in
        choice = util.choose_random(configuration.STRINGS_HUG)
        reply = choice.format(hugger=hugger, target=target)
    # Make a fancy embed so people don't complain about getting pinged twice
    R, G, B = 256 * 256, 256, 1
    embed = discord.Embed(
        description=reply,
    colour=(46*R + 204*G + 113*B)
    )
    # Done
    await message.channel.send(embed=embed)

    if str(client.user.id) in target:
        await message.channel.send('Thanks for hugging me; I love that!')

@command({
    "syntax": "replytome [text to echo]",
    "category": Category.OTHER,
    "description": "Replies to you"
})
async def replytome(message: discord.Message, parameters: str, client: discord.Client) -> None:
    if parameters == "":
        text = util.choose_random(("ok", "no"))
    else:
        text = parameters
    await message.channel.send(content=text, reference=message)


@command({
    "syntax": "aa",
    "aliases": ["a"*a for a in range(1, 12)],
    "description": "AAAAAAAAAAAAAAAAAA",
    "category": Category.OTHER
})
async def aa(message: discord.Message, parameters: str, client: discord.Client) -> None:
    await message.channel.send(content="AAAAAAAAAAAAAAAAAAAAAAAA", reference=message)


@command({
    "syntax": "villager <message>",
    "aliases": ["h" + "m"*i for i in range(1, 6)],
    "description": "Translates a message to villager",
    "category": Category.OTHER
})
async def villager(message: discord.Message, parameters: str, client: discord.Client) -> None:
    """Villager command by LeeSpork
    Originally developed for Obsidion bot
    """
    last_was_alpha = False  # Was the last character part of the alphabet? Used to detect the start of a word
    last_was_h = False  # Was the last character converted to an H or h? Used to prevent 'H's without 'm's
    last_was_lower_m = False  # Was the last character converted to a lowercase m? Used to make "HmmHmm" instead of "HmmMmm"
    sentence = "" # Output string
    original_sentance = parameters

    for char in original_sentance:

        if char.isalpha():  # Is it an alphabetical letter? If so, replace with 'Hmm'

            if not last_was_alpha:  # First letter of alphabetical string
                sentence += "H" if char.isupper() else "h"
                last_was_h = True
                last_was_lower_m = False

            else:  # Non-first letter
                if not char.isupper():
                    sentence += "m"
                    last_was_lower_m = True
                    last_was_h = False
                else:
                    # Use an 'H' instead to allow CamelCase 'HmmHmm's
                    if last_was_lower_m:
                        sentence += "H"
                        last_was_h = True
                    else:
                        sentence += "M"
                        last_was_h = False
                    last_was_lower_m = False

            last_was_alpha = True  # Remember for next potential 'M'

        else:  # Non-alphabetical letters -- Do not replace
            # Add an m after 'H's without 'm's
            if last_was_h:
                sentence += "m"
                last_was_h = False
            # Add non-letter character without changing it
            sentence += char
            last_was_alpha = False

    # If the laster character is an H, add a final 'm'
    if last_was_h:
        sentence += "m"
    
    await message.channel.send(content=sentence)
