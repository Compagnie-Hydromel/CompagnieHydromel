import discord

from libs.config import Config
from libs.databases.models.guild_user import GuildUser
from libs.utils.role_utils import RoleUtils


class LevelUtils():
    @staticmethod
    async def add_point(member: discord.Member, amount: int = 1):
        user = GuildUser.from_user_discord_id_and_guild_discord_id(
            str(member.id), str(member.guild.id))
        old_level = user.level
        user.point += amount
        user.monthly_point += amount * 2
        user.save()
        if old_level != user.level:
            await member.send("Congratulations! You have reached level " + str(user.level) + "!")
            await RoleUtils.update_role(member, user)
