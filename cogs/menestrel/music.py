import traceback
import discord
import os
from discord.components import Component
from discord.ui.item import Item
import wavelink

from libs.config import Config
from libs.exception.music.not_connected_to_voice_channel_exception import NotConnectedToVoiceChannelException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.server_music_manger import ServerMusicManager
from libs.log import Log, LogType

class Music(discord.Cog):    
    def __init__(self, bot) -> None:
        self.__bot = bot
        self.__music_config = Config().value["music"]
        self.__server_music_manager = ServerMusicManager()
    
    @discord.Cog.listener()
    async def on_ready(self):
        await self.lavalink_nodes_connect()

    async def lavalink_nodes_connect(self):
        """Connect to our Lavalink nodes."""
        
        await wavelink.NodePool.create_node(
            bot=self.__bot,
            host=self.__music_config["lavalink_ip"],
            port=self.__music_config["lavalink_port"],
            password=os.getenv("LAVALINK_PASSWORD")
        ) 

    @discord.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        music_manager = self.__server_music_manager.get(player.guild.id)
        try:
            if reason != "REPLACED":
                await music_manager.skip()
        except NothingLeftInQueueException:
            await music_manager.disconnect()
        except:
            Log(traceback.format_exc(), LogType.ERROR)

    @discord.slash_command(description="Command that can play music that we want.")
    @discord.option("search", description="Search or youtube link")
    async def play(self, ctx : discord.ApplicationContext, *, search: str):
        try:
            music_manager = self.__server_music_manager.get(ctx.guild.id)
            song = await music_manager.search(search)
            player_displayer = PlayerDisplayer()
            await music_manager.play(ctx.author.voice, song)
            await ctx.respond(embed=player_displayer.embed, view=player_displayer)
        except NotConnectedToVoiceChannelException:
            pass
        except:
            Log(traceback.format_exc(), LogType.ERROR)

    @discord.slash_command(description="Command that stop the music and make the bot leave the channel.")
    async def stop(self, ctx : discord.ApplicationContext):
        try: 
            await self.__server_music_manager.get(ctx.guild.id).stop()
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            
    @discord.slash_command(description="Command that pause the music.")
    async def pause(self, ctx : discord.ApplicationContext):
        try:
            await self.__server_music_manager.get(ctx.guild.id).pause()
        except:
            Log(traceback.format_exc(), LogType.ERROR)
        
    @discord.slash_command(description="Command that resume the music.")
    async def resume(self, ctx : discord.ApplicationContext):
        try:
            await self.__server_music_manager.get(ctx.guild.id).resume()
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            
    @discord.slash_command(description="Command that skip the music.")
    async def skip(self, ctx : discord.ApplicationContext):
        try:
            await self.__server_music_manager.get(ctx.guild.id).skip()
        except NothingLeftInQueueException:
            pass
        except:
            Log(traceback.format_exc(), LogType.ERROR)
    
    @discord.slash_command(description="Command that get the queue. (max 6 music show)")
    async def queue(self, ctx : discord.ApplicationContext):
        pass
        
    @discord.slash_command(description="Command to get the current music.")
    async def now(self, ctx : discord.ApplicationContext):
        pass

def setup(bot):
    if Config().value["music"]["enable"]:
        if os.getenv("LAVALINK_PASSWORD") == None:
            Log("No lavalink password found.")
        else: 
            bot.add_cog(Music(bot))
            
class PlayerDisplayer(discord.ui.View):
    message = None
    def __init__(self) -> None:
        super().__init__()
    
    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed(title="Player", description="", color=0x2F3136)
        embed.set_footer(text="Music player")
        return embed
    
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏮") 
    async def back(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        await self.refresh(interaction.response)
    
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏯") 
    async def play(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        await self.refresh(interaction.response)
    
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏭") 
    async def skip(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        await self.refresh(interaction.response)
    
    async def refresh(self, response: discord.message.Message):
        await response.edit_message(embed=self.embed)