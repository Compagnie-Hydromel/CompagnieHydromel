import discord

from libs.databases.model.roles.roles import Roles
from libs.databases.model.user.users import Users
from libs.exception.role.role_not_exist_exception import RoleNotExistException

class RoleUtils():
    @staticmethod
    async def remove_all_roles(member: discord.Member):
        for one_role in Roles().all:
            role: discord.Role = discord.utils.get(member.guild.roles, id=int(one_role.discord_id))
            if role in member.roles:
                await member.remove_roles(role)

    @staticmethod
    async def add_role(member: discord.Member, user):
        roles = Roles()
        if user.has_accepted_rules:
            for role_level in reversed(range(1, user.level + 1)):
                try:
                    role: discord.Role = discord.utils.get(member.guild.roles, id=int(roles.by_level(role_level).discord_id))
                    if role not in member.roles:
                        await member.add_roles(role)
                    break
                except RoleNotExistException:
                    continue

    @staticmethod
    async def update_role(member: discord.Member, user):
        await RoleUtils.remove_all_roles(member)
        await RoleUtils.add_role(member, user)

    @staticmethod
    async def update_all_user_role(guild: discord.guild) -> None:
        for user in Users().all:
            await RoleUtils.update_role(discord.utils.get(guild.members, id=int(user.discord_id)), user)