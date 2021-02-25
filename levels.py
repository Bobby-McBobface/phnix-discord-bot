import asyncio
import data
import configuration

chatted = []

async def add_exp(member):
  global chatted
  
  if member not in chatted:
    chatted.append(member)

    try:
      data.level_dict[member] += configuration.XP_GAIN_PER_MESSAGE
    except KeyError:
      # They haven't chatted before
      data.level_dict[member] = configuration.XP_GAIN_PER_MESSAGE
    finally:
      data.save_data(data.level_dict, 'data/levels.txt')

# Need a non blocking loop here to reset chatted every INTERVAL seconds
async def clear_chatted_loop():
    global chatted
    
    while True:
        await asyncio.sleep(configuration.XP_MESSAGE_INTERVAL)
        chatted = []

