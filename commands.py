import configuration

async def test(message):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.command_data = {
  "syntax": "test",
  "aliases": ["twoplustwo"],
  "role_requirements": [configuration.MODERATOR_ROLE]
}

async def pad(msg):
    """Spaces out your text"""
    cmd_arguments = msg.content.split(maxsplit=1)[1:]
    await msg.channel.send(" ".join(cmd_arguments))
pad.command_data = {
  "syntax": "pad <text>",
  "aliases": [],
  "role_requirements": []
}
