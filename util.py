async def split_into_member_and_reason(parameters:str) -> tuple:
    """Splits parameters into member and reason, used for most moderation commands."""
    if parameters == None:
        return (None, None)
    
    split_params = parameters.split(maxsplit=1)
    
    member_text = split_params[0] # There always will be a string here
    
    try:
        member_id = int(member_text.strip('<@!>'))
    except ValueError:
        member_id = None
        
    try: 
        reason = split_params[1]
    except IndexError:
        reason = None
        
    return (member_id, reason)
  
async def check_for_and_strip_prefixes(string:str, prefixes:tuple) -> str:
    """If `string` starts with one of the given prefixes, return the string sans the prefix. Otherwise, returns None."""
    for prefix in prefixes:
        if string.startswith(prefix):
            return string[len(prefix):].lstrip()
    # If the loop ended, it failed to find a prefix
    return None

class warning():
  pass
 
    
                
