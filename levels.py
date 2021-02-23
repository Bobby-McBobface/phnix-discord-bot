import asyncio
import level_dict
interval = 20 # Seconds
chatted = []

async def level_up(member):
  if member not in chatted:
    #logic here
    chatted.append(member)
  
  
