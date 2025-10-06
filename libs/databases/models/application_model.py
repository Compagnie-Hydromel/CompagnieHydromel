from MIWOS.model import Model


class ApplicationModel(Model):
    @staticmethod
    def set_bot(bot):
        ApplicationModel.bot = bot

    @staticmethod
    def get_bot():
        return ApplicationModel.bot
