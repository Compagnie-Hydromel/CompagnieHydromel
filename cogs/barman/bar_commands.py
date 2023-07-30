from io import BytesIO
import traceback
import discord
from libs.config import Config
from libs.databases.user import User
from libs.exception.not_enougt_smartcoin_exception import NotEnougtSmartcoinException
from libs.log import Log, LogType
from libs.utils import Utils

class BarCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot
        self.__config = Config()

    @discord.slash_command(name="beer", description="Get your beer but it cost some smartcoin")
    async def beer(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "beer")
            
    @discord.slash_command(name="soft", description="Get your soft but it cost some smartcoin")
    async def soft(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "soft")
    
    @discord.slash_command(name="hydromel", description="Get some hydrmel but it cost some smartcoin")
    async def hydromel(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "hydromel")
        
    @discord.slash_command(name="water", description="Get some free water")
    async def water(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "water")
                    
    async def handler(self, ctx: discord.commands.context.ApplicationContext, drink: str):
        Log(ctx.author.name + " is launching " + drink + " commands", LogType.COMMAND)
        try:
            price = self.__config.value["bar_commands"][drink]["price"]
            list_of_url = self.__config.value["bar_commands"][drink]["list"]
            
            img_file = discord.File(Utils().download_image_with_list_random(list_of_url), drink + ".png")
            
            if price > 0:
                self.__payement_process(User(str(ctx.author.id)), price)
                await ctx.respond("Little " + drink + " (Warning " + str(price) + " smartcoin the " + drink + ")", file=img_file)
            else: 
                await ctx.respond(file=img_file)
        except NotEnougtSmartcoinException:
            await ctx.respond("You don't have enougth smartcoin for a " + drink + " (Minimal price: " + str(price) + " smartcoin)")
        except:
            await ctx.respond("An error has occurred, no " + drink + " for you now.")
            Log(traceback.format_exc(), LogType.ERROR)
    
    def __payement_process(self, user: User, price: int):
        barman = User(str(self._bot.user.id))
        
        user.remove_smartcoin(price)
        barman.add_smartcoin(price) 

def setup(bot: discord.bot.Bot):
    bot.add_cog(BarCommands(bot))