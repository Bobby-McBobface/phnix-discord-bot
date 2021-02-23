import asyncio
import
interval = 20 # Seconds
chatted = []

async def level_up(member):
  if member not in chatted:
    
    chatted.append(member)
  
  
