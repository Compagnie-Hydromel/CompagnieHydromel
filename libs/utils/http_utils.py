from fastapi import HTTPException, Request
import discord

from libs.databases.models.application_model import ApplicationModel
from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.user import User


class HTTPUtils:
    @staticmethod
    def get_user_from_session(request: Request) -> User:
        user = User.find(request.session.get("user_id", None))
        if not user:
            raise HTTPException(
                status_code=401, detail="No active session found.")
        return user

    @staticmethod
    async def get_guild_admin_from_session(request: Request, guild_id: int) -> Guild:
        user = HTTPUtils.get_user_from_session(request)
        guild = Guild.find(guild_id)
        if guild is None:
            raise HTTPException(status_code=404, detail="Guild not found")
        member = await HTTPUtils.sync_guild_admin(user, guild)
        if not member.is_admin:
            raise HTTPException(
                status_code=403, detail="Administrator permission required")
        return guild

    @staticmethod
    async def sync_guild_admin(user, guild):
        bot = getattr(ApplicationModel, "bot", None)
        if bot is None or not bot.is_ready():
            raise HTTPException(status_code=503, detail="Discord is not ready")
        discord_guild = bot.get_guild(int(guild.discord_id))
        if discord_guild is None:
            raise HTTPException(status_code=403, detail="Guild is unavailable")
        try:
            member = await discord_guild.fetch_member(int(user.discord_id))
        except (discord.NotFound, discord.Forbidden):
            stored_member = GuildUser.whereFirst(user=user, guild=guild)
            if stored_member is not None and stored_member.is_admin:
                stored_member.is_admin = False
                stored_member.saveOrFail()
            raise HTTPException(
                status_code=403, detail="Discord access denied")
        except discord.HTTPException:
            raise HTTPException(
                status_code=503, detail="Discord is unavailable")
        stored_member = GuildUser.from_user_and_guild(user, guild)
        is_admin = bool(member.guild_permissions.administrator)
        if bool(stored_member.is_admin) != is_admin:
            stored_member.is_admin = is_admin
            stored_member.saveOrFail()
        return stored_member
