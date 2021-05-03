from abc import ABC, abstractmethod
from enum import Enum

import discord


class Permission:
    permissions: discord.Permissions = discord.Permissions()
    requiredRoles: list[str] = []

    def __init__(self, permissions: discord.Permissions = discord.Permissions(), required_roles: list[str] = []):
        self.permissions = permissions
        self.requiredRoles = required_roles


class Parameter:
    identifier: str = ""
    required: bool = False

    def __init__(self, identifier: str, required: bool = False):
        self.identifier = identifier
        self.required = required


class CategoryData:
    friendlyName: str = ''
    priority: int = -1

    def __init__(self, friendlyName: str, priority: int = -1):
        self.friendlyName = friendlyName
        self.priority = priority


class Category(Enum):
    MODERATION = CategoryData('Moderation', 10)
    GENERAL = CategoryData('General')
    LEVELING = CategoryData('Leveling')
    DEVELOPMENT = CategoryData('Bot Development', 100)
    OTHER = CategoryData('Other')


class Command(ABC):
    command: str = ""
    description: str = ""
    category: Category = Category.OTHER
    alias: list[str] = []
    parameters: list[Parameter] = []
    required_permissions: Permission = Permission()

    def __init__(self, command: str, description: str, alias: list[str] = [], parameters: list[Parameter] = [], required_permissions: Permission = Permission(), category: Category = Category.OTHER):
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
