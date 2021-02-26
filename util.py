async def split_into_member_and_reason(parameters):
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
  
class warning():
  pass

    
                
