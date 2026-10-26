import traceback
import discord

from libs.exception.handler import Handler
from libs.music.guild_music_manager import GuildMusicManager
from libs.log import Log
from libs.paginator import Paginator
from libs.music.music_player_displayer import MusicPlayerDisplayer
from libs.music.control_server import MusicControlServer
from libs.music.music_manager import Track
from libs.music.radios import radio_choices


async def radio_autocomplete(ctx):
    needle = ctx.value.casefold()
    return [discord.OptionChoice(name=radio["name"], value=radio["id"])
            for radio in radio_choices() if needle in radio["name"].casefold()][:25]


class Music(discord.Cog):
    def __init__(self, bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()
        self.__guild_music_manager = GuildMusicManager()
        self.__control_server = MusicControlServer(bot, self.__guild_music_manager)

    def cog_unload(self):
        self.__bot.loop.create_task(self.__control_server.close())

    async def cog_before_invoke(self, ctx):
        try:
            if ctx.guild is None:
                raise ValueError("Cette commande nécessite un serveur Discord.")
            if ctx.command.name in ("play", "radio", "stop", "pause", "resume", "back", "skip"):
                self.__guild_music_manager.get(ctx.guild.id).authorize(ctx.author)
        except Exception as error:
            # Pycord only dispatches DiscordException subclasses from pre-hooks.
            raise discord.ApplicationCommandInvokeError(error) from error

    async def cog_command_error(self, ctx, error):
        error = getattr(error, "original", error)
        message = str(error) if isinstance(error, ValueError) else self.__error_handler.response_handler(error, traceback.format_exc())
        await ctx.respond(message, ephemeral=True)

    @discord.Cog.listener()
    async def on_ready(self):
        await self.__control_server.start()

    @discord.slash_command(description="Command that can play music that we want.")
    @discord.option("search", description="Titre, lien YouTube/SoundCloud ou identifiant radio (ex. fip)")
    @discord.option("source", choices=["youtube", "soundcloud", "radio"], default="youtube")
    async def play(self, ctx: discord.ApplicationContext, search: str, source: str = "youtube"):
        await self._play(ctx, search, source)

    @discord.slash_command(description="Écouter une radio de la liste proposée.")
    @discord.option("station", description="Radio à écouter", autocomplete=radio_autocomplete)
    async def radio(self, ctx: discord.ApplicationContext, station: str):
        await self._play(ctx, station, "radio")

    async def _play(self, ctx, search, source):
        Log.command(ctx.author.name +
                    " is launching play commands with " + search)
        try:
            await ctx.defer()

            music_manager = self.__guild_music_manager.get(ctx.guild.id)
            song = await music_manager.search(search, source)
            music_manager.authorize(ctx.author)
            player_displayer = MusicPlayerDisplayer(music_manager)

            await music_manager.play(ctx.author.voice, song)
            await ctx.respond(embed=player_displayer.embed, view=player_displayer)
        except Exception as e:
            await ctx.respond(str(e) if isinstance(e, ValueError) else self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that stop the music and make the bot leave the channel.")
    async def stop(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching stop commands")
        try:
            await self.__guild_music_manager.get(ctx.guild.id).stop()
            await ctx.respond("Music stopped and bot left the voice channel.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that pause the music.")
    async def pause(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching pause commands")
        try:
            await self.__guild_music_manager.get(ctx.guild.id).pause()
            await ctx.respond("Music paused.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that resume the music.")
    async def resume(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching resume commands")
        try:
            await self.__guild_music_manager.get(ctx.guild.id).resume()
            await ctx.respond("Music resumed.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that come back to the previous music.")
    async def back(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching back commands")
        try:
            await ctx.defer()

            await self.__guild_music_manager.get(ctx.guild.id).back()
            await ctx.respond("Going back to the previous music.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that skip the music.")
    async def skip(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching skip commands")
        try:
            await ctx.defer()

            await self.__guild_music_manager.get(ctx.guild.id).skip()
            await ctx.respond("Music skipped.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command that get the queue.")
    async def queue(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching queue commands")
        try:
            songs = self.__guild_music_manager.get(ctx.guild.id).queue

            paginator = Paginator(self.__generate_pages(songs), "Queues")
            await ctx.respond(embed=paginator.embed, view=paginator)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Command to get the current music.")
    async def now(self, ctx: discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching now commands")
        try:
            music_manager = self.__guild_music_manager.get(ctx.guild.id)
            player_displayer = MusicPlayerDisplayer(music_manager)

            await ctx.respond(embed=player_displayer.embed, view=player_displayer)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    def __generate_pages(self, songs: list[Track]) -> list:
        pages = []
        song_per_page = 3
        counter = 0
        content = ""
        for song in songs:
            content += ("**[" + str(song) + "](" + song.uri +
                        ")**\n" + song.author + "\n\n")

            counter += 1
            if counter >= song_per_page:
                pages.append(content)
                content = ""
                counter = 0

        if content != "":
            pages.append(content)
        return pages


def setup(bot):
    bot.add_cog(Music(bot))
