import traceback
import discord
import os
import wavelink

from libs.config import Config
from libs.exception.handler import Handler
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.music.guild_music_manager import GuildMusicManager
from libs.log import Log, LogType
from libs.paginator import Paginator
from libs.music.music_player_displayer import MusicPlayerDisplayer

class Music(discord.Cog):    
    def __init__(self, bot) -> None:
        self.__bot = bot
        self.__config = Config()
        self.__music_config = self.__config.value["music"]
        self.__response = self.__config.value["response"]
        self.__guild_music_manager = GuildMusicManager()
        self.__error_handler = Handler()
    
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
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        music_manager = self.__guild_music_manager.get(player.guild.id)
        try: 
            Log("Playing " + track.info['uri'] + " in " + player.channel.name)
        except:
            Log(traceback.format_exc(), LogType.ERROR)

    @discord.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        try:
            match reason:
                case "LOAD_FAILED":
                    Log("Load failed in " + player.channel.name, LogType.ERROR)
                case "FINISHED":
                    await self.__guild_music_manager.get(player.guild.id).skip(old_song=track)
                    Log("Skipping music in " + player.channel.name)
        except NothingLeftInQueueException:
            await self.__guild_music_manager.get(player.guild.id).disconnect()
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
            player_displayer = MusicPlayerDisplayer(music_manager)
            
            await music_manager.play(ctx.author.voice, song)
            await ctx.respond(embed=player_displayer.embed, view=player_displayer)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that stop the music and make the bot leave the channel.")
    async def stop(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching stop commands", LogType.COMMAND)
        try: 
            await self.__guild_music_manager.get(ctx.guild.id).stop()
            await ctx.respond(self.__response["music_stopping"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            
    @discord.slash_command(description="Command that pause the music.")
    async def pause(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching pause commands", LogType.COMMAND)
        try:
            await self.__guild_music_manager.get(ctx.guild.id).pause()
            await ctx.respond(self.__response["pausing_music"].replace("{music}", str(self.__guild_music_manager.get(ctx.guild.id).now)))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
        
    @discord.slash_command(description="Command that resume the music.")
    async def resume(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching resume commands", LogType.COMMAND)
        try:
            await self.__guild_music_manager.get(ctx.guild.id).resume()
            await ctx.respond(self.__response["resuming_music"].replace("{music}", str(self.__guild_music_manager.get(ctx.guild.id).now)))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
    @discord.slash_command(description="Command that come back to the previous music.")
    async def back(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching back commands", LogType.COMMAND)
        try:
            await ctx.defer()
            
            await self.__guild_music_manager.get(ctx.guild.id).back()
            await ctx.respond(self.__response["back_to_previous_music"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that skip the music.")
    async def skip(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching skip commands", LogType.COMMAND)
        try:
            await ctx.defer()
            
            await self.__guild_music_manager.get(ctx.guild.id).skip()
            await ctx.respond(self.__response["skipping_music"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
    @discord.slash_command(description="Command that get the queue.")
    async def queue(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching queue commands", LogType.COMMAND)
        try:
            songs =  self.__guild_music_manager.get(ctx.guild.id).queue
            
            paginator = Paginator(self.__generate_pages(songs), "Queues")
            await ctx.respond(embed=paginator.embed, view=paginator)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
        
    @discord.slash_command(description="Command to get the current music.")
    async def now(self, ctx : discord.ApplicationContext):
        Log(ctx.author.name + " is launching now commands", LogType.COMMAND)
        try:
            music_manager = self.__guild_music_manager.get(ctx.guild.id)
            player_displayer = MusicPlayerDisplayer(music_manager)
            
            await ctx.respond(embed=player_displayer.embed, view=player_displayer)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            

    def __generate_pages(self, songs: list[wavelink.abc.Playable]) -> list:
        pages = []
        song_per_page = 3
        counter = 0
        content = ""
        songs.reverse()
        for song in songs:
            content += ("**[" + str(song) + "](" + song.info["uri"] + ")**\n" + song.info["author"] + "\n\n")
            
            counter += 1
            if counter > song_per_page:
                pages.append(content)
                content = ""
                counter = 0
            
        if content != "":
            pages.append(content)
        return pages

def setup(bot):
    if Config().value["music"]["enable"]:
        if os.getenv("LAVALINK_PASSWORD") == None:
            Log("No lavalink password found.", LogType.WARNING)
        else: 
            bot.add_cog(Music(bot))