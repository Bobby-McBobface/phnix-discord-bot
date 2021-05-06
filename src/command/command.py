from abc import ABC, abstractmethod
from enum import Enum
from config import config

import discord


class Permission:
    def __init__(self, permissions: discord.Permissions = discord.Permissions(), required_roles: set = set()):
        self.permissions = permissions
        if required_roles == set():
            self.required_roles = {config['guildId']}
        else:
            self.required_roles = required_roles


class Parameter:
    def __init__(self, identifier: str, required: bool = False):
        self.identifier = identifier
        self.required = required

class Category(Enum):
    MODERATION = {
        'friendly_name': 'Moderation', 
        'priority': 10
    }
    GENERAL = {
        'friendly_name': 'General', 
        'priority': -1
    }
    LEVELING = {
        'friendly_name': 'Leveling', 
        'priority': -1
    }
    DEVELOPMENT = {
        'friendly_name': 'Bot Development', 
        'priority': 100
    }
    OTHER = {
        'friendly_name': 'Other', 
        'priority': -1
    }


class Command(ABC):
    command: str = ""
    description: str = ""
    category: Category = Category.OTHER
    alias: list = []
    parameters: list = []
    required_permissions: Permission = Permission()

    def __init__(self, command: str, description: str, alias: list = [], parameters: list = [], required_permissions: Permission = Permission(), category: Category = Category.OTHER):
        self.description = description
        self.category = category
        self.command = command
        self.alias = alias
        self.parameters = parameters
        self.required_permissions = required_permissions

    # noinspection PyMethodParameters
    @abstractmethod
    async def execute(self, message: discord.Message, parameters: str, client: discord.Client):
        pass
