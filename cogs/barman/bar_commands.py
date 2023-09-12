from io import BytesIO
import traceback
import discord
from libs.config import Config
from libs.databases.user import User
from libs.exception.smartpoint.not_enougt_smartpoint_exception import NotEnougtSmartpointException
from libs.log import Log, LogType
from libs.paginator import Paginator
from libs.utils import Utils

class BarCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()

    @discord.slash_command(description="Buy your beer with smartpoint")
    async def beer(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "beer")
            
    @discord.slash_command(description="Buy your soft drink with smartpoint")
    async def soft(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "soft")
    
    @discord.slash_command(description="Buy your hydromel with smartpoint")
    async def hydromel(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "hydromel")
        
    @discord.slash_command(description="Get some free water")
    async def water(self, ctx: discord.commands.context.ApplicationContext):
        await self.handler(ctx, "water")
                    
    async def handler(self, ctx: discord.commands.context.ApplicationContext, drink: str):
        Log(ctx.author.name + " is launching " + drink + " commands", LogType.COMMAND)
        try:
            drinks_in_config = self.__config.value["bar_commands"][drink]
            price = drinks_in_config["price"]
            list_of_url = drinks_in_config["list"]
            
            img_file = discord.File(Utils().download_image_with_list_random(list_of_url), drink + ".png")
            
            user = User(str(ctx.author.id))
            
            if price > 0:
                self.__payement_process(user, price)
                await ctx.respond("Little " + drink, file=img_file)
                user.add_point(10)
                user.increase_number_of_buy()
            else: 
                await ctx.respond(file=img_file)
            
        except NotEnougtSmartpointException:
            await ctx.respond(self.__config.value["exception_response"]["not_enougth_smartpoint_for_a_drinks"].replace("{drink}", drink).replace("{price}", str(price)))
        except:
            await ctx.respond(self.__config.value["exception_response"]["default"])
            Log(traceback.format_exc(), LogType.ERROR)
            
    @discord.slash_command(name="drinks_menu", description="Get the list of selled drinks")
    async def drinks(self, ctx: discord.commands.context.ApplicationContext):
        paginator = Paginator(self.__generate_pages(), "Drinks Menu", 0xd1911b)
        
        await ctx.respond(
            view = paginator, 
            embed = paginator.embed
        ) 
    
    def __payement_process(self, user: User, price: int):
        barman = User(str(self.__bot.user.id))
        
        user.remove_smartpoint(price)
        barman.add_smartpoint(price) 
        
    def __generate_pages(self) -> list:
        pages = []
        
        bar_commands_config = self.__config.value["bar_commands"]
        beer_price: str = str(bar_commands_config["beer"]["price"])
        soft_price: str = str(bar_commands_config["soft"]["price"])
        hydromel_price: str = str(bar_commands_config["hydromel"]["price"])
        water_price: str = str(bar_commands_config["water"]["price"])
        pages.append("**Beer** \n" + beer_price + " smartpoint" + "\n\n" + 
                     "**Soft** \n" + soft_price + " smartpoint" + "\n\n" + 
                     "**Hydromel** \n" + hydromel_price + " smartpoint" + "\n\n" + 
                     "**Water** \n" + water_price + " smartpoint")
        
        return pages

def setup(bot: discord.bot.Bot):
    bot.add_cog(BarCommands(bot))