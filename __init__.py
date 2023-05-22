from enum import Enum
from . import misc
from . import moderation
from . import level
from . import system

# Custom exceptions we can raise
class CommandSyntaxError(Exception):
    pass


class Category(Enum):
    MODERATION = {
        'friendly_name': 'Moderation',
        'priority': 10
    }
    LEVELING = {
        'friendly_name': 'Leveling',
        'priority': 1
    }
    DEVELOPMENT = {
        'friendly_name': 'Bot Development',
        'priority': 100
    }
    SYSTEM = {
        'friendly_name': 'System commands',
        'priority': 50
    }
    OTHER = {
        'friendly_name': 'Other',
        'priority': -1
    }


# --------------------------------------------------#
# COMMAND LIST POPULATOR #
# --------------------------------------------------#

command_list = []
command_aliases_dict = {}

'''Decorator factory to register commands
Make a command by decorating a function with
@command({
   "syntax": "command syntax",
   (optionally) "role_requirements": set{role id},
   "category": Category.SOME_CATEGORY,
   "description": "the help to show up on the help menu"
   "allowed_channels": list[channel id]
})'''

command_list = []
command_aliases_dict = {}


def command(cmdinfo):
    # Set stuff to default values
    cmdinfo["aliases"] = cmdinfo.get("aliases", [])
    cmdinfo["allowed_channels"] = cmdinfo.get("allowed_channels", [])
    cmdinfo["category"] = cmdinfo.get("category", Category.OTHER)

    def actual_decorator(cmdfunc):
        cmdfunc.command_data = cmdinfo
        command_list.append(cmdfunc)
        command_aliases_dict[cmdfunc.__name__] = cmdfunc
        for alias in cmdinfo["aliases"]:
            command_aliases_dict[alias.lower()] = cmdfunc
        return cmdfunc

    return actual_decorator




# Sort command list by priority for help
command_list.sort(
    key=lambda a: a.command_data["category"].value["priority"], reverse=True)
