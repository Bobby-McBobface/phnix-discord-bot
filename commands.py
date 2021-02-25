import configuration
import data
import main

#--------------------------------------------------#
# MISC COMMANDS #
#--------------------------------------------------#
async def test(message, parameters):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.command_data = {
  "syntax": "test",
  "aliases": ["twoplustwo"],
  "role_requirements": [configuration.MODERATOR_ROLE, configuration.COOL_ROLE]
}

async def pad(message, parameters):
    """Spaces out your text"""
    if parameters == None:
        await message.channel.send("Usage: `pad <message>`")
    else:
        await message.channel.send(" ".join(parameters))
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

#--------------------------------------------------#
# LEVEL COMMANDS #
#--------------------------------------------------#
async def rank(msg):
    try:
        await msg.channel.send(data.level_dict[msg.author.id])
    except KeyError:
        await msg.channel.send("You aren't ranked yet! Send some messages first and try again later")
rank.command_data = {
  "syntax": "rank",
  "aliases": [],
  "role_requirements": [configuration.EVERYONE_ROLE]
}
