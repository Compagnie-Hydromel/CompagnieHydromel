import traceback

import discord

from libs.exception.bot_exception import BotException
from libs.exception.music.no_music_playing_exception import NoMusicPlayingException
from libs.exception.music.no_playing_instance_exception import NoPlayingInstanceException
from libs.log import Log
from libs.music.music_manager import MusicManager


class MusicPlayerDisplayer(discord.ui.View):
    def __init__(self, music_manager: MusicManager):
        super().__init__()
        self.__music_manager = music_manager

    async def interaction_check(self, interaction):
        try:
            self.__music_manager.authorize(interaction.user)
            return True
        except Exception:
            await interaction.response.send_message(
                "Rejoignez le salon vocal du Ménestrel pour le contrôler.", ephemeral=True)
            return False

    @property
    def embed(self):
        song = self.__music_manager.now
        seconds = song.length // 1000
        duration = f"{seconds // 60}:{seconds % 60:02d}" if seconds else "En direct"
        embed = discord.Embed(
            title="En pause ⏸" if self.__music_manager.is_paused else "En lecture 🎶", color=0x2F3136)
        embed.add_field(name="Titre", value=f"[{song.title}]({song.uri})", inline=True)
        embed.add_field(name="Artiste", value=song.author, inline=True)
        embed.add_field(name="Durée", value=duration, inline=True)
        embed.set_footer(text="source: " + song.source)
        return embed

    async def _control(self, interaction, action):
        # Stream resolution can take longer than Discord's 3-second deadline.
        await interaction.response.defer()
        try:
            if action == "toggle":
                action = "resume" if self.__music_manager.is_paused else "pause"
            await getattr(self.__music_manager, action)()
        except NoPlayingInstanceException:
            pass
        except BotException as error:
            await interaction.followup.send(error.message, ephemeral=True)
        except Exception:
            Log.error(traceback.format_exc())
            await interaction.followup.send("Commande musicale impossible.", ephemeral=True)
        finally:
            await self.refresh(interaction)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏮")
    async def back(self, button, interaction):
        await self._control(interaction, "back")

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏯")
    async def play(self, button, interaction):
        await self._control(interaction, "toggle")

    @discord.ui.button(style=discord.ButtonStyle.danger, emoji="⏹")
    async def stop(self, button, interaction):
        await self._control(interaction, "stop")

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⏭")
    async def skip(self, button, interaction):
        await self._control(interaction, "skip")

    async def refresh(self, interaction):
        try:
            await interaction.edit_original_response(embed=self.embed)
        except (NoPlayingInstanceException, NoMusicPlayingException):
            await interaction.edit_original_response(content="Aucune musique en cours.", embed=None, view=None)
