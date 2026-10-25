from MIWOS.model import Model
import discord


class ApplicationModel(Model):
    @staticmethod
    def set_bot(bot: discord.bot.Bot):
        ApplicationModel.bot: discord.bot.Bot = bot

    @staticmethod
    def get_bot() -> discord.bot.Bot:
        return ApplicationModel.bot
