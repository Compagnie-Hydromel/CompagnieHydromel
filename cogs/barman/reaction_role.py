import discord

from libs.config import Config
from libs.databases.models.role import Role
from libs.databases.models.guild_user import GuildUser
from libs.log import Log
from libs.utils.role_utils import RoleUtils


class ReactionRole(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()

    @discord.Cog.listener()
    async def on_raw_reaction_add(self, added_reaction: discord.RawReactionActionEvent) -> None:
        if self.__config.value["reactions"]["enable"]:
            for reaction in self.__config.value["reactions"]["list"]:
                # membre
                await self.add_role_with_reaction(added_reaction, reaction["message_id"], reaction["emoji"], reaction["role_id"], reaction["action"])

    @discord.Cog.listener()
    async def on_raw_reaction_remove(self, added_reaction: discord.RawReactionActionEvent) -> None:
        if self.__config.value["reactions"]["enable"]:
            for reaction in self.__config.value["reactions"]["list"]:
                # membre
                await self.remove_role_with_reaction(added_reaction, reaction["message_id"], reaction["emoji"], reaction["role_id"], reaction["action"])

    @discord.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        databaseRole = Role.from_discord_id(role.id)
        if not databaseRole:
            return

        databaseRole.delete()
        await RoleUtils.update_all_user_role(role.guild)

    async def add_role_with_reaction(self, reaction: discord.RawReactionActionEvent, message_id: int, emoji: str, role_id: int, action: str) -> None:
        """This method is designed to add a role with a reaction.

        Args:
            reaction (discord.RawReactionActionEvent): The new reaction.
            message_id (int): The attended message id.
            emoji (str): The attended emoji.
            role_id (int): The role id to add.
        """
        if (reaction.message_id == message_id and reaction.emoji.name == emoji):
            match(action):
                case "accept_rules":
                    user = GuildUser.from_user_discord_id_and_guild_discord_id(
                        reaction.user_id, reaction.guild_id)
                    user.has_accepted_rules = True
                    user.save()
                    await RoleUtils.add_role(reaction.member, user)

                case "emoji_to_role" | _:
                    try:
                        role: discord.role = discord.utils.get(
                            reaction.member.guild.roles, id=role_id)
                        await reaction.member.add_roles(role)
                    except:
                        Log.warning(f"Role {role_id} not found")

    async def remove_role_with_reaction(self, reaction: discord.RawReactionActionEvent, message_id: int, emoji: str, role_id: int, action: str) -> None:
        """This method is designed to remove a role with a reaction.

        Args:
            reaction (discord.RawReactionActionEvent): The just removed reaction.
            message_id (int): The attended message id.
            emoji (str): The attended emoji.
            role_id (int): The role id to remove.
        """
        guild = self.__bot.get_guild(reaction.guild_id)
        if (reaction.message_id == message_id and reaction.emoji.name == emoji):
            member: discord.Member = discord.utils.get(
                guild.members, id=reaction.user_id)
            match action:
                case "accept_rules":
                    user: GuildUser = GuildUser.from_user_discord_id_and_guild_discord_id(
                        reaction.user_id, reaction.guild_id)
                    user.has_accepted_rules = False
                    user.save()
                    await RoleUtils.remove_all_roles(member)
                case "emoji_to_role" | _:
                    try:
                        role: discord.Role = discord.utils.get(
                            guild.roles, id=role_id)
                        await member.remove_roles(role)
                    except:
                        Log.warning(f"Role {role_id} not found")


def setup(bot: discord.bot.Bot):
    bot.add_cog(ReactionRole(bot))
