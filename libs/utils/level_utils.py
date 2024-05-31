import discord

from libs.config import Config
from libs.databases.model.user.user import User
from libs.utils.role_utils import RoleUtils

class LevelUtils():
    @staticmethod
    async def add_point(member: discord.Member, amount: int = 1):
        user = User(str(member.id))
        old_level = user.level
        user.add_point(amount)
        if old_level != user.level:
            await member.send(Config().value["response"]["level_up"].replace("{level}", str(user.level)))
            await RoleUtils.update_role(member, user)