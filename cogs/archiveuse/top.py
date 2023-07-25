import traceback
import discord

from libs.databases.user import User
from libs.log import Log, LogType

class Top(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot        

    @discord.slash_command(name="top", description="")
    async def top(self, ctx):
        Log(ctx.author.name + " is launching top commands", LogType.COMMAND)
        try:
            list_of_best_users = User(str(ctx.author.id)).get_top_users()
            message = ""
            for user in list_of_best_users:
                username = self._bot.get_user(int(user[0])).name
                message += f"{username} : {user[1]}\n" 
            
            await ctx.respond(embed = discord.Embed(title="Top player", description=message, color=0x75E6DA))
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured")

def setup(bot):
    bot.add_cog(Top(bot))