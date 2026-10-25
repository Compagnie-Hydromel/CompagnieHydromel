import os
import traceback
import discord

from libs.databases.models.user import User
from libs.exception.handler import Handler


class WebCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    @discord.slash_command(description="Get the web dashboard link")
    async def web(self, ctx: discord.ApplicationContext) -> None:
        try:
            await ctx.defer()

            user = User.from_discord_id(ctx.author.id)

            token = user.generate_authorization_token()

            url = f"{os.getenv('APP_URL', 'http://127.0.0.1:8000')}/api/sessions?authorization={token}"

            message = f"You can access the web dashboard here: {url}"

            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.respond("The web dashboard link was sent to your private messages.")
                await ctx.author.send(message)
            else:
                await ctx.respond(message)

        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))


def setup(bot: discord.bot.Bot):
    bot.add_cog(WebCommands(bot))
