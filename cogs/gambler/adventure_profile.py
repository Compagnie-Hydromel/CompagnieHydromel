import discord # type: ignore
from libs.exception.handler import Handler

from libs.log import Log
import traceback

class AdventureProfile(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    @discord.slash_command(description="Get your beautiful adventure profile")
    async def adventure_profile(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching adventure_profile command")
        try:
            # WARNING message in french, is this ok ?
            await ctx.respond("""
Pour le moment je ne peux pas accéder à la base de données, veuillez attendre que bebou finisse le refactor.
En attendant je peux vous montrer à quoi ressemblerait un profile type :
```
Username : <username>
Level : <level> ; <nbXp> / <nbXpLvl>
HP : <hp> | Gold : <gold> 
```
""")
        
            """
            await ctx.defer()

            user = User(str(ctx.author.id))
            
            Log.info("create adventure profile for " + str(ctx.author))
            adv_profile = 
            """


        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

def setup(bot: discord.bot.Bot):
    bot.add_cog(AdventureProfile(bot))
