import asyncio
import data
INTERVAL = 30 # Seconds apart messages have to be
EXP_RATE = 5 # Per message
chatted = []

async def add_exp(member):
  global chatted
  
  if member not in chatted:
    chatted.append(member)
    # Need to save the data as well
    try:
      data.level_dict[member] += EXP_RATE
    except KeyError:
      # They haven't chatted before
      data.level_dict[member] = EXP_RATE

# Need a non blocking loop here to reset chatted every INTERVAL seconds
async def clear_chatted_loop():
    global chatted
    
    while True:
        await asyncio.sleep(INTERVAL)
        chatted = []

