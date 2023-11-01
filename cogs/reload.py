import discord 
import os
from libs.config import Config

from libs.databases.user import User 

class Reload(discord.Cog):
    bot : discord.bot.Bot
    
    def __init__(self, bot):
        self.bot = bot
        self.__config = Config()
        self.__response_exception = self.__config.value["exception_response"]
    
    @discord.command(name="reload", help="Reload all cogs")
    async def reload(self, ctx):
        if User(str(ctx.author.id)).is_root:    
            extensions = self.bot.extensions.copy()
            for extension in extensions:
                self.bot.reload_extension(extension)
            await ctx.respond("Reloaded all cogs")
        else: 
            await ctx.respond(self.__response_exception["not_root"])

def setup(bot):
    bot.add_cog(Reload(bot))