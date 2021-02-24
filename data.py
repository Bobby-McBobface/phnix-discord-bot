level_dict = {
  # Format: User ID: XP amount
  # Also add the current level and amount to next level so we don't have recalculate each time
  # https://www.desmos.com/calculator/yjvvpuq1jn
}

warn_dict = {
  # Format: User ID: [Warning1, Warning2]
  # Warning object: <Reason for warn, Timestamp>
}

mute_dict = {
  # Format: User ID: {Timestamp: Unmute timestamp, Previous roles: [Previous role1, Previous role2]
}
