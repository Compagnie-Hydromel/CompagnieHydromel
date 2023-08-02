import discord
from time import sleep
import wavelink
import os

class Music(discord.Cog):
    def __init__(self, bot) -> None:
        self.__bot = bot
    
    @discord.Cog.listener()
    async def on_ready(self):
        await self.lavalink_nodes_connect()
        
    async def lavalink_nodes_connect(self):
        """Connect to our Lavalink nodes."""
        
        await wavelink.NodePool.create_node(
            bot=self.__bot,
            host=os.getenv("LAVALINK_IP"),
            port=os.getenv("LAVALINK_PORT"),
            password=os.getenv("LAVALINK_PASSWORD")
        ) 

    @discord.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        pass

    @discord.slash_command(description="Commande qui permet de faire jouer au bot la musique que l'on souhaite")
    @discord.option("search", description="Nom ou lien youtube de la musique")
    async def play(self, ctx : discord.ApplicationContext, *, search: str):
        pass

    @discord.slash_command(description="Commande qui permet d'arrêter la musique. Cette commande fait également le bot quitter le salon.")
    async def stop(self, ctx : discord.ApplicationContext):
        pass
    
    @discord.slash_command(description="Commande qui permet de mettre en pause la musique.")
    async def pause(self, ctx : discord.ApplicationContext):
        pass
    
    @discord.slash_command(description="Commande permettant de sauter la musique actuelle.")
    async def skip(self, ctx : discord.ApplicationContext):
        pass
    
    @discord.slash_command(description="Commande qui permet de voir les prochaines musiques (max 6) présentes dans la liste d'attente.")
    async def queue(self, ctx : discord.ApplicationContext):
        pass
        
    @discord.slash_command(description="Commande qui permet de voir quel musique est actuellement jouée.")
    async def now(self, ctx : discord.ApplicationContext):
        pass

def setup(bot):
    bot.add_cog(Music(bot))