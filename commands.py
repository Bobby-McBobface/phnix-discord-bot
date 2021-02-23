import configuration

async def test(message):
    """A command named 'test'"""
    result = 2 + 2
    await message.channel.send(f"Two plus two is {result}")
test.metadata = {
  "syntax": "test",
  "aliases": ["twoplustwo"],
  "role_requirements": [configuration.MODERATOR_ROLE]
}

async def pad(msg):
    """Spaces out your text"""
    await msg.channel.send(" ".join(msg.content))
pad.metadata = {
  "syntax": "pad <text>",
  "aliases": [],
  "role_requirements": []
}
