async def split_into_member_and_reason(parameters:str) -> tuple:
    """Splits parameters into member and reason, used for most moderation commands."""
    split_params = parameters.split(maxsplit=1)
    try:
        member_text = split_params[0]
        member_text.strip('<@!>')
    except IndexError:
        # Syntax error! No need to procede
        return (None, None)
   
    member = get_member(int(member_text))  
    try: 
        reason = split_params[1]
    except IndexError:
        reason = None
        
    return (member, reason)
  
def check_for_and_strip_prefixes(string:str, prefixes:tuple) -> str:
    """If `string` starts with one of the given prefixes, return the string sans the prefix. Otherwise, returns None."""
    for prefix in prefixes:
        if string.startswith(prefix):
            return string[len(prefix):].lstrip()
    # If the loop ended, it failed to find a prefix
    return None

class warning():
  pass

    
                
