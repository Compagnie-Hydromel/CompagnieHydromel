import traceback
import discord
from math import floor
from libs.exception.music.no_playing_instance_exception import NoPlayingInstanceException
from libs.exception.music.nothing_left_in_back_queue import NothingLeftInBackQueueException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.log import Log

from libs.music.music_manager import MusicManager


class MusicPlayerDisplayer(discord.ui.View):
    message = None

    def __init__(self, music_manager: MusicManager) -> None:
        self.__music_manager = music_manager
        super().__init__()

    @property
    def embed(self) -> discord.Embed:
        current_music_info = self.__music_manager.now
        embed = discord.Embed(
            title="Now playing 🎶",
            color=0x2F3136
        )
        duration_seconds = current_music_info.length / 1000
        duration_minutes = duration_seconds / 60
        duration_seconds = (duration_minutes - floor(duration_minutes)) * 60
        duration = str(floor(duration_minutes)) + ":" + \
            str(floor(duration_seconds))

        embed.add_field(
            name="Title", value="[" + current_music_info.title + "](" + current_music_info.uri + ")", inline=True)
        embed.add_field(
            name="Author", value=current_music_info.author, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.set_footer(text="source: " + current_music_info.source)
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
            Log.error(traceback.format_exc())
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
            Log.error(traceback.format_exc())

    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="⏹")
    async def stop(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        try:
            await self.__music_manager.stop()
        except NoPlayingInstanceException:
            pass
        except:
            Log.error(traceback.format_exc())
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
            Log.error(traceback.format_exc())
        finally:
            await self.refresh(interaction.response)

    async def refresh(self, response: discord.message.Message):
        try:
            await response.edit_message(embed=self.embed)
        except NoPlayingInstanceException:
            await response.edit_message(content="No music playing.", embed=None, view=None)
