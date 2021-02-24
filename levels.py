import data
INTERVAL = 2 # Seconds apart messages have to be
EXP_RATE = 5 # Per message
chatted = []

async def add_exp(member):
  if member not in chatted:
    chatted.append(member)
    # Need to save the data as well
    try:
      data.level_dict[member] += exp_rate
    except KeyError:
      # They haven't chatted before
      data.level_dict[member] = exp_rate

# Need a non blocking loop here to reset chatted every INTERVAL seconds
  

