import traceback
import discord
import os
from discord.components import Component
from discord.ui.item import Item
import wavelink
from math import floor

from libs.config import Config
from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.exception.music.no_music_playing import NoMusicPlaying
from libs.exception.music.no_playing_instance_exception import NoPlayingInstanceException
from libs.exception.music.no_result_found_exception import NoResultsFoundException
from libs.exception.music.not_connected_to_voice_channel_exception import NotConnectedToVoiceChannelException
from libs.exception.music.nothing_left_in_back_queue import NothingLeftInBackQueueException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.guild_music_manger import GuildMusicManager
from libs.log import Log, LogType
from libs.music_manager import MusicManager

class Music(discord.Cog):    
    def __init__(self, bot) -> None:
        self.__bot = bot
        self.__music_config = Config().value["music"]
        self.__guild_music_manager = GuildMusicManager()
    
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
        music_manager = self.__guild_music_manager.get(player.guild.id)
        try:
            match reason:
                case "REPLACED":
                    pass
                case _:
                    await music_manager.skip()
                    Log("Skipping music in " + player.channel.name)
        except NothingLeftInQueueException:
            await music_manager.disconnect()
            Log("Disconnect bot in " + player.channel.name)
        except:
            Log(traceback.format_exc(), LogType.ERROR)

    @discord.slash_command(description="Command that can play music that we want.")
    @discord.option("search", description="Search or youtube link")
    async def play(self, ctx : discord.ApplicationContext, *, search: str):
        Log(ctx.author.name + " is launching play commands with " + search, LogType.COMMAND)
        try:
            await ctx.defer()
            
            music_manager = self.__guild_music_manager.get(ctx.guild.id)
            song = await music_manager.search(search)
            player_displayer = PlayerDisplayer(music_manager)
            
            await music_manager.play(ctx.author.voice, song)
            await ctx.respond(embed=player_displayer.embed, view=player_displayer)
        except AlreadyPlayingException:
            await ctx.respond("Already playing. Adding to queue.")
        except NotConnectedToVoiceChannelException:
            await ctx.respond("You need to be connected to a voice channel to play music.")
        except NoResultsFoundException:
            await ctx.respond("No results found.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")

    @discord.slash_command(description="Command that stop the music and make the bot leave the channel.")
    async def stop(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching stop commands", LogType.COMMAND)
        try: 
            await self.__guild_music_manager.get(ctx.guild.id).stop()
            await ctx.respond("Stopping.")
        except NoPlayingInstanceException:
            await ctx.respond("The bot is not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")
            
    @discord.slash_command(description="Command that pause the music.")
    async def pause(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching pause commands", LogType.COMMAND)
        try:
            await self.__guild_music_manager.get(ctx.guild.id).pause()
            await ctx.respond("Pausing music: `" + str(self.__guild_music_manager.get(ctx.guild.id).now) + "`")
        except NoPlayingInstanceException:
            await ctx.respond("The bot not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")
        
    @discord.slash_command(description="Command that resume the music.")
    async def resume(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching resume commands", LogType.COMMAND)
        try:
            await self.__guild_music_manager.get(ctx.guild.id).resume()
            await ctx.respond("Resuming music: `" + str(self.__guild_music_manager.get(ctx.guild.id).now) + "`")
        except NoPlayingInstanceException:
            await ctx.respond("The bot not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")
    
    @discord.slash_command(description="Command that come back to the previous music.")
    async def back(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching back commands", LogType.COMMAND)
        try:
            await ctx.defer()
            
            await self.__guild_music_manager.get(ctx.guild.id).back()
            await ctx.respond("Back to the previous music.")
        except NothingLeftInBackQueueException:
            await ctx.respond("Nothing left in previous song queue.")
        except NoPlayingInstanceException:
            await ctx.respond("The bot not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")

    @discord.slash_command(description="Command that skip the music.")
    async def skip(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching skip commands", LogType.COMMAND)
        try:
            await ctx.defer()
            
            await self.__guild_music_manager.get(ctx.guild.id).skip()
            await ctx.respond("Skipping.")
        except NothingLeftInQueueException:
            await ctx.respond("Nothing left in queue.")
        except NoPlayingInstanceException:
            await ctx.respond("The bot not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")
    
    @discord.slash_command(description="Command that get the queue. (max 6 music show)")
    async def queue(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching queue commands", LogType.COMMAND)
        try:
            raise NotImplementedError
        except NoPlayingInstanceException:
            await ctx.respond("The bot not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")
        
    @discord.slash_command(description="Command to get the current music.")
    async def now(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching now commands", LogType.COMMAND)
        try:
            current_music = self.__guild_music_manager.get(ctx.guild.id).now
            await ctx.respond(current_music.info)
        except NoMusicPlaying:
            await ctx.respond("No music playing.")
        except NoPlayingInstanceException:
            await ctx.respond("The bot not playing music.")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured!")
    
    def __message_musics_in_queue(self) -> discord.Embed:
        message = discord.Embed(
            title="Liste d'attente",
            colour=0xffffff
        )
        
        for idx, music in enumerate(self.__music_queue[1:], start=1):
            if idx > 6:
                break
            
            message.add_field(
                name=f"{idx}:",
                value=f"[{music[0].title}]({music[0].uri})",
            )
        
        return message

def setup(bot):
    if Config().value["music"]["enable"]:
        if os.getenv("LAVALINK_PASSWORD") == None:
            Log("No lavalink password found.")
        else: 
            bot.add_cog(Music(bot))
            
class PlayerDisplayer(discord.ui.View):
    message = None
    def __init__(self, music_manager: MusicManager) -> None:
        self.__music_manager = music_manager
        super().__init__()
    
    @property
    def embed(self) -> discord.Embed: 
        current_music_info = self.__music_manager.now.info
        embed = discord.Embed(
            title="Now playing 🎶",  
            color=0x2F3136
        )
        duration_minutes = self.__music_manager.now.duration / 60
        duration_seconds = (duration_minutes - floor(duration_minutes)) * 60
        duration = str(floor(duration_minutes)) + ":" + str(floor(duration_seconds))
        
        embed.add_field(name="Title", value="[" + current_music_info["title"] + "](" + current_music_info["uri"] + ")", inline=True)
        embed.add_field(name="Author", value=current_music_info["author"], inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.set_footer(text="source: " + current_music_info["sourceName"])
        return embed
        
        
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏮") 
    async def back(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        try:
            await self.__music_manager.back()
        except NoPlayingInstanceException:
            pass
        except NothingLeftInBackQueueException:
            pass
        except:
            Log(traceback.format_exc(), LogType.ERROR)
        finally:
            await self.refresh(interaction.response)
                        
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏯") 
    async def play(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        try: 
            if self.__music_manager.is_paused:
                await self.__music_manager.resume()
            else:
                await self.__music_manager.pause()
            await self.refresh(interaction.response)
        except NoPlayingInstanceException:
            pass
        except:
            Log(traceback.format_exc(), LogType.ERROR)
    
    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="⏹")
    async def stop(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        try: 
            await self.__music_manager.stop()
        except NoPlayingInstanceException:
            pass
        except:
            Log(traceback.format_exc(), LogType.ERROR)
        finally:
            await self.refresh(interaction.response)
            
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏭") 
    async def skip(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        try:
            await self.__music_manager.skip()
        except NothingLeftInQueueException:
            pass
        except NoPlayingInstanceException:
            pass
        except:
            Log(traceback.format_exc(), LogType.ERROR)
        finally:
            await self.refresh(interaction.response)
    
    async def refresh(self, response: discord.message.Message):
        try: 
            await response.edit_message(embed=self.embed)
        except NoPlayingInstanceException:
            await response.edit_message(content="No music playing.", embed=None, view=None)