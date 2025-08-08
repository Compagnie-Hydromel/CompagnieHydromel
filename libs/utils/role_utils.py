import discord

from libs.databases.models.guild_user import GuildUser
from libs.exception.role.role_not_exist_exception import RoleNotExistException
from libs.databases.models.role import Role
from libs.databases.models.guild import Guild


class RoleUtils():
    @staticmethod
    async def remove_all_roles(member: discord.Member):
        for one_role in Guild.from_discord_id(member.guild.id).roles:
            role: discord.Role = discord.utils.get(
                member.guild.roles, id=int(one_role.discord_id))
            if role in member.roles:
                await member.remove_roles(role)

    @staticmethod
    async def add_role(member: discord.Member, user: GuildUser):
        if GuildUser.has_accepted_rules:
            for role_level in reversed(range(1, user.level + 1)):
                try:
                    role: discord.Role = discord.utils.get(
                        member.guild.roles, id=int(Role.by_level(role_level).discord_id))
                    if role not in member.roles:
                        await member.add_roles(role)
                    break
                except RoleNotExistException:
                    continue

    @staticmethod
    async def update_role(member: discord.Member, user: GuildUser):
        await RoleUtils.remove_all_roles(member)
        await RoleUtils.add_role(member, user)

    @staticmethod
    async def update_all_user_role(guild: discord.guild) -> None:
        for guild_user in Guild.from_discord_id(guild.id).guild_users:
            try:
                await RoleUtils.update_role(discord.utils.get(guild.members, id=int(guild_user.user.discord_id)), guild_user)
            except:
                continue
