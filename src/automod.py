import discord
import configuration
import util

async def automod(message: discord.Message) -> bool:
    # Returns True if message is dealt with, False otherwise

    if util.check_mod_or_test_server(message):
        return False

    return await filter_words(message)


async def filter_words(message: discord.Message) -> bool:
    # word blacklist
    text_lowercase = message.content.lower()
    # Iterate through all words in the blacklist
    for word in configuration.WORDS_CENSORED:
        # Make word lowercase to avoid always false match on listed words with capitalized letters
        if word.lower() in text_lowercase:
            # Store the content before we delete it
            original_content = message.content
            # Delete messages containing items in WORDS_CENSORED
            await message.delete()
            # DM the user what their original message was
            # with a fancy embed thing
            censored_word_embed = discord.Embed(
                description="Your message was deleted because it contained a blacklisted word."
            ).add_field(name="Your message", value=original_content)
            await message.author.send(embed=censored_word_embed)
            # Do not continue processing this message
            return True
    return False
