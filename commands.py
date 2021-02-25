import configuration

#--------------------------------------------------#
# MISC COMMANDS #
#--------------------------------------------------#
async def test(message):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.command_data = {
  "syntax": "test",
  "aliases": ["twoplustwo"],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

async def pad(msg):
    """Spaces out your text"""
    try:
        # Get all text after first whitespace character
        command_argument = msg.content.split(maxsplit=1)[1]
    except IndexError:
        await msg.channel.send("Usage: `pad <message>`")
    else:
        await msg.channel.send(" ".join(command_argument))
pad.command_data = {
  "syntax": "pad <message>",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}

#--------------------------------------------------#
# MODERATION COMMANDS #
#--------------------------------------------------#
'''async def warn():
    pass

async def mute():
    pass

async def kick():
    pass

async def ban():
    pass'''
