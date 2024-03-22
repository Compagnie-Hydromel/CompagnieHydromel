import traceback
import discord
from libs.config import Config

from libs.databases.model.user.users import Users
from libs.exception.handler import Handler
from libs.log import Log

class Top(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot  
        self.__error_handler = Handler()

    @discord.slash_command(description="Get the top level up player")
    async def top(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching top commands")
        try:
            list_of_best_users = Users().get_top_users
            message = ""
            for user in list_of_best_users:
                user_id = None
                try:  # to avoid error if discord_id is not an convertible in int
                    user_id = int(user.discord_id)
                except: 
                    continue
                
                discord_user = self.__bot.get_user(user_id)
                
                if discord_user is None:
                    continue
                else:
                    username = discord_user.name
                
                message += f"**{username}** is level {user.level}\n\n" 
            
            await ctx.respond(embed = discord.Embed(title="Top player", description=message, color=0x75E6DA))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

def setup(bot: discord.bot.Bot):
    bot.add_cog(Top(bot))