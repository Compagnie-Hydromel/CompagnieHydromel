import discord

from libs.log import Log


class Listener(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.__bot = bot

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        Log.message(message.channel, message.content,
                    message.author.name, self.__bot.user.name, onlyDm=True)

        if message.author == self.__bot.user:
            return

    @discord.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_content = "deleted a message : " + message.content
        Log.message(message.channel, log_content,
                    message.author.name, self.__bot.user.name, onlyDm=True)

    @discord.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log_content = "edited a message : " + before.content + " -> " + after.content
        Log.message(before.channel, log_content, before.author.name,
                    self.__bot.user.name, onlyDm=True)


def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))
