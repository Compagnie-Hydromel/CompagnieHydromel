import discord

from libs.databases.models.guild_user import GuildUser
from libs.databases.models.role import Role
from libs.databases.models.guild import Guild
from libs.log import Log


class RoleUtils():
    @staticmethod
    async def remove_all_roles(member: discord.Member, roles=None, keep_role=None):
        if roles is None:
            roles = Guild.from_discord_id(
                member.guild.id).roles.whereNotNull("level")
        for one_role in roles:
            role: discord.Role = discord.utils.get(
                member.guild.roles, id=int(one_role.discord_id))
            if role is not None and role != keep_role and role in member.roles:
                await member.remove_roles(role)

    @staticmethod
    def _eligible_role(member: discord.Member, user: GuildUser):
        if user.has_accepted_rules:
            guild = Guild.from_discord_id(member.guild.id)
            eligible = sorted((role for role in guild.roles.whereNotNull("level")
                               if role.level <= user.level), key=lambda role: role.level, reverse=True)
            for db_role in eligible:
                role: discord.Role = discord.utils.get(
                    member.guild.roles, id=int(db_role.discord_id))
                if role is None:
                    continue
                return role
        return None

    @staticmethod
    async def add_role(member: discord.Member, user: GuildUser):
        role = RoleUtils._eligible_role(member, user)
        if role is not None and role not in member.roles:
            await member.add_roles(role)

    @staticmethod
    async def update_role(member: discord.Member, user: GuildUser):
        role = RoleUtils._eligible_role(member, user)
        # Keep the correct role in place: Discord's member cache may not reflect
        # a removal immediately, so removing then re-adding it is unreliable.
        await RoleUtils.remove_all_roles(member, keep_role=role)
        if role is not None and role not in member.roles:
            await member.add_roles(role)

    @staticmethod
    async def update_all_user_role(guild: discord.Guild, removed_roles=None) -> dict:
        result = {"updated": 0, "failed": 0, "skipped": 0}
        for guild_user in Guild.from_discord_id(guild.id).guildusers:
            member = guild.get_member(int(guild_user.user.discord_id))
            if member is None:
                result["skipped"] += 1
                continue
            try:
                for role in removed_roles or []:
                    if role in member.roles:
                        await member.remove_roles(role)
                await RoleUtils.update_role(member, guild_user)
                result["updated"] += 1
            except Exception as error:
                result["failed"] += 1
                Log.warning(
                    f"Could not synchronize roles for {member.id}: {error}")
        return result

    @staticmethod
    def emoji_matches(actual, configured):
        if not configured:
            return False
        expected = discord.PartialEmoji.from_str(configured)
        if expected.id is not None:
            return actual.id == expected.id
        return actual.name == configured
