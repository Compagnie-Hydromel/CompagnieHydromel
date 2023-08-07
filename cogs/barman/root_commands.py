import traceback
import discord
from libs.config import Config
from libs.databases.user import User
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.log import Log, LogType
from libs.utils import Utils

class RootCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()

    @discord.slash_command(description="Broadcast a message to a any channel")
    @discord.option("channel", discord.abc.GuildChannel, require=True)
    @discord.option("message", require=True)
    async def broadcast(self, ctx: discord.commands.context.ApplicationContext, channel: discord.abc.GuildChannel, message: str):
        Log(ctx.author.name + " is launching broadcast commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            if not isinstance(channel, discord.abc.Messageable):
                await ctx.respond("This channel is not messageable!")
                return
            
            await channel.send(message.replace("\\n", "\n"))
            await ctx.respond("Message sent!")
        except:
            await ctx.respond("An error has occurred, cannot send message now.")
            Log(traceback.format_exc(), LogType.ERROR)
            
    @discord.slash_command(description="Send informations in information channel")
    @discord.option("message", require=True)
    @discord.option("title", require=False)
    @discord.option("color", require=False)
    async def info(self, ctx: discord.commands.context.ApplicationContext, message: str, title: str = "Information", color: str = "#ffffff"):
        Log(ctx.author.name + " is launching info commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            information_channel = self.__bot.get_channel(self.__config.value["information_channel_id"])
            if information_channel == None:
                await ctx.respond("Information channel not found! please add it in config.yml")
                return
            if not isinstance(information_channel, discord.abc.Messageable):
                await ctx.respond("The information channel is not messageable! please change it in config.yml")
                return
            
            # WARNING: eval = evil 
            # we check it before to avoid security issue
            embed = discord.Embed(title=title, description=message.replace("\\n", "\n"), color=eval("0x" + Utils().check_color(color)))
            
            await information_channel.send(embed=embed)
            await ctx.respond("Message sent!")
        except ColorNotCorrectException:
            await ctx.respond("The color is not correct! please use hexadecimal color (ex: #ffffff) or use color name (green, blue, red, yellow, orange, pink, black, white, ect...)")
        except:
            await ctx.respond("An error has occurred, cannot send message now.")
            Log(traceback.format_exc(), LogType.ERROR)

    async def __check_if_root(self, ctx: discord.commands.context.ApplicationContext) -> bool:
        if not User(str(ctx.author.id)).is_root():
            await ctx.respond("You are not root!")
            return False
        return True

def setup(bot: discord.bot.Bot):
    bot.add_cog(RootCommands(bot))