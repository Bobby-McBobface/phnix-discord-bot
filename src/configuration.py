PREFIX = "!"

VERSION = "1.7.5"

MODERATOR_ROLE = 329226272683065346
GUILD_ID = 329226224759209985
EVERYONE_ROLE = 329226224759209985
MUTED_ROLE = 465873110911156224

WELCOME_CHANNEL = 464772278526148629
FAREWELL_CHANNEL = 464772278526148629
FEED_CHANNEL = 329851820509888513

YOUTUBE_PING = 793548066699083786
TWITCH_PING = 782326457325322251

TWITCH_CHANNEL_ID = 82826005

TWITCH_SLEEP = 60 * 1.5
YOUTUBE_SLEEP = 60 * 1.5

ALLOWED_COMMAND_CHANNELS = [329235461929435137, 334929304561647617]
DEFAULT_COMMAND_CHANNEL = 329235461929435137

# Level/EXP system
XP_MESSAGE_INTERVAL = 60  # SecondS
XP_GAIN_MIN = 19
XP_GAIN_MAX = 21

LEVEL_ROLES = {
    "netherite1": [731769341246177340, 65],
    "stack": [847681970539724851, 64],
    "netherite": [731769341246177340, 55],
    "emerald": [420174387166314506, 45],
    "obsidian": [630748573990125595, 40],
    "diamond": [337152398415888385, 35],
    "gold": [337151525325635586, 30],
    "lapis": [804091179146412052, 25],
    "copper": [630748385925922856, 20],
    "iron": [337151464592113664, 15],
    "stone": [804093931397840906, 10],
    "wood": [337151269523423236, 5]
}

DISALLOWED_XP_GAIN = [329235461929435137, 334929304561647617]

# Mute
TIME_MULIPLIER = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    '_': 2635200,  # 30.5 days in a month
    'y': 31557600  # 365.25 days in a year
}

# sequence of characters that shouldn't be someone's entire nickname
INVISIBLE_CHARACTERS = " ᲼"

# Messages
STRINGS_HUG = [
    "{hugger} hugs {target}",
    "{hugger} gives a big hug to {target}",
    "{hugger} 🫂 {target}"
]

STRINGS_PUN = [
    "{hugger} tried to self-hug; gets tangled up",
    "{hugger} couldn't figure out how to hug themselves"
]

########################
# Preformatted Strings #
########################
welcome_msg = "{} has joined the game!"
farewell_msg = "{} has left the game."
