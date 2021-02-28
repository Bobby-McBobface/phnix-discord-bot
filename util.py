import discord

async def split_into_member_and_reason(message, parameters:str) -> tuple:
    """
    Splits parameters into member and reason.
    Used for most moderation commands.
    """
    
    if parameters == None:
        return (None, None)
    
    try:     
        split_params = parameters.split(maxsplit=1)
        member = message.guild.get_member(int(split_params[0].strip('<@!>')))
        try: 
            reason = split_params[1].lstrip('| ')
        except IndexError:
            reason = None
        
    except ValueError:
        # Reversed to split the last | in case someone has | in their name
        split_params_pipe = parameters[::-1].split("|", 1)
        
        member = message.guild.get_member_named(
            split_params_pipe[1][::-1].rstrip())
        
        try: 
            reason = split_params_pipe[0][::-1].lstrip()
        except IndexError:
            reason = None
            
    return (member, reason)
  
async def check_for_and_strip_prefixes(string:str, prefixes:tuple) -> str:
    """
    If `string` starts with one of the given prefixes,
    return the string and the prefix. Otherwise, returns None.
    """
    
    for prefix in prefixes:
        if string.startswith(prefix):
            return string[len(prefix):].lstrip()
    # If the loop ended, it failed to find a prefix
    return None
    
                
