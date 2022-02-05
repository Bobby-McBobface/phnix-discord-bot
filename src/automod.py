import discord
import configuration
import util
import re
import jellyfish
from urllib.parse import urlparse
import asyncio
import logger

async def automod(message: discord.Message, client: discord.Client) -> bool:
    # Returns True if message is dealt with, False otherwise

    if util.check_mod_or_test_server(message):
        return False

    if await filter_words(message):
        return True
    
    if await phishing_check(message):
        
        phishing_link_embed = discord.Embed(
                description="Your message was deleted because a phishing link was detected."
            ).add_field(name="Your message", value=message.content)
        await message.author.send(embed=phishing_link_embed)
        
        await logger.log_misc("Phishing check triggered", f"{message.author.mention}\n\n{message.content}", client)
        
        return True
    
    return False



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


    
async def phishing_check(message: discord.Message) -> bool:
    
    # Converting the message into a python string
    msg_string = message.content            
    
    # Testing for and extracting urls from the message
    url_match = re.search("(?P<url>https?:\/[^\s]+)", msg_string)
    
    if url_match is None:
        return False
    else:
        url = url_match.group("url")
        
    if "@everyone" in msg_string:
        await message.delete()
        return True
    
    # Splitting the URL into parts, namely link eg. "foobar.co.uk" and top level domain eg, "foobar"
    domain = urlparse(url).netloc
    domain_parts = domain.split(".")
    
    # Bypassing known-good links that return a false positive
    if domain in configuration.DOMAIN_WHITELIST:
        return False
    
    # Running a word similarity test on the top level domain, comparing it to "discord". (Lower = more similar)
    # https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
    distance = jellyfish.damerau_levenshtein_distance(domain_parts[0], 'discord')
    
    # If the distance is 0, the domain is "discord", which isn't used by any illegitemate website
    if distance == 0:
        return False
    
    # Distances lower than 3 are highly likely to be phising. This includes addresses like diacord.gift or dlisord.com
    if distance <= 3:
        await message.delete()
        return True
    
    # Distances lower than 5 are still likely to be phising, but also have high false positive rates, so are sent for secondary checking
    elif distance <= 5:
        return await secondary_phising_check(message)
    
    # At distances over 5, it's unlikely that a link mascarades as "discord", although composite links ("discord-nitro-gift.site") may go through due to size
    else:
        return False
    
    return False

async def secondary_phising_check(message: discord.Message) -> bool:
    
    # The secondary check looks at the context of the message to determine if it's suspicious enough to remove
    
    
    # Sleeping asynchronously to give time to discord to load website embeds onto the message
    await asyncio.sleep(1)
    
    # Refreshing the message
    fresh_msg = await message.channel.fetch_message(message.id)
    
    # Checking for the appearance of keywords within the message embed
    if fresh_msg.embeds:
        title = fresh_msg.embeds[0].title
        embed_suspicious_vocabulary = ("nitro", "discord")
        
        try:
            for word in embed_suspicious_vocabulary:
                if word in title.lower():
                    await message.delete()
                    return True
        except AttributeError:
            pass
    
    # Similarly, checking for more specific combinations of keywords in the message body
    suspicious_message_words = ("@everyone", "free nitro", "discord nitro")
    msg_string = message.content.lower()
    
    for word in suspicious_message_words:
        if word in msg_string:
            await message.delete()
            return True
    
    return False
            
