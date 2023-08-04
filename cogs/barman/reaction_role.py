
import discord

from libs.config import Config

class ReactionRole(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()
        
    @discord.Cog.listener()
    async def on_raw_reaction_add(self, added_reaction: discord.RawReactionActionEvent) -> None:
        if self.__config.value["reactions"]["enable"]:
            for reaction in self.__config.value["reactions"]["list"]: 
                await self.add_role_with_reaction(added_reaction, reaction["message_id"], reaction["emoji"], reaction["role_id"]) # membre    
        
    @discord.Cog.listener()
    async def on_raw_reaction_remove(self, added_reaction: discord.RawReactionActionEvent) -> None:
        if self.__config.value["reactions"]["enable"]:
            for reaction in self.__config.value["reactions"]["list"]: 
                await self.remove_role_with_reaction(added_reaction, reaction["message_id"], reaction["emoji"], reaction["role_id"]) # membre
        
    async def add_role_with_reaction(self, reaction: discord.RawReactionActionEvent, message_id: int, emoji: str, role_id: int) -> None:
        """This method is designed to add a role with a reaction.

        Args:
            reaction (discord.RawReactionActionEvent): The new reaction.
            message_id (int): The attended message id.
            emoji (str): The attended emoji.
            role_id (int): The role id to add.
        """
        if(reaction.message_id == message_id and reaction.emoji.name == emoji):
            role = discord.utils.get(reaction.member.guild.roles, id=role_id)
            await reaction.member.add_roles(role)

    async def remove_role_with_reaction(self, reaction: discord.RawReactionActionEvent, message_id: int, emoji: str, role_id: int) -> None:
        """This method is designed to remove a role with a reaction.

        Args:
            reaction (discord.RawReactionActionEvent): The just removed reaction.
            message_id (int): The attended message id.
            emoji (str): The attended emoji.
            role_id (int): The role id to remove.
        """
        guild = self.__bot.get_guild(reaction.guild_id)
        if(reaction.message_id == message_id and reaction.emoji.name == emoji):
            role = discord.utils.get(guild.roles, id=role_id)
            member = discord.utils.get(guild.members, id=reaction.user_id)
            await member.remove_roles(role)

def setup(bot: discord.bot.Bot):
    bot.add_cog(ReactionRole(bot))