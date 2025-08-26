import traceback
import discord

from libs.databases.models.guild import Guild
from libs.exception.handler import Handler
from libs.log import Log
from libs.utils.level_utils import LevelUtils


class Listener(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        Log.message(message.channel, message.content,
                    message.author.name, self.__bot.user.name)

        if message.author == self.__bot.user:
            return

        guild = Guild.from_discord_id(message.guild.id)

        try:
            if message.type == discord.MessageType.premium_guild_subscription:
                information_channel_id = int(guild.information_channel_id)
                if information_channel_id != 0:
                    await self.__bot.get_channel(information_channel_id).send("" + str(message.author) + " has boosted the server! Thank you for your support! 🎉")
        except Exception as e:
            self.__error_handler.response_handler(e, traceback.format_exc())

    @discord.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_content = "a message was deleted from " + \
            str(message.author) + " | " + \
            str(message.author.id) + " : " + message.content
        Log.info(log_content)

    @discord.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log_content = "edited a message : " + before.content + " -> " + after.content
        Log.message(before.channel, log_content,
                    before.author.name, self.__bot.user.name)

    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        Log.info(member.name + " joined the server " + member.guild.name)
        await LevelUtils.add_point(member)

    @discord.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        Log.info(member.name + " left the server " + member.guild.name)

    @discord.Cog.listener()
    async def on_raw_reaction_add(self, added_reaction: discord.RawReactionActionEvent) -> None:
        Log.info("Reaction " + str(added_reaction.emoji) + " added by " + str(added_reaction.member) +
                 " in " + str(added_reaction.channel_id) + " on message " + str(added_reaction.message_id))

    @discord.Cog.listener()
    async def on_raw_reaction_remove(self, added_reaction: discord.RawReactionActionEvent) -> None:
        username = self.__bot.get_user(added_reaction.user_id).name
        Log.info("Reaction " + str(added_reaction.emoji) + " removed by " + username + " in " +
                 str(added_reaction.channel_id) + " on message " + str(added_reaction.message_id))


def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))
