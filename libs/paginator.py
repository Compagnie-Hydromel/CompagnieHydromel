import discord

class Paginator(discord.ui.View):
    __pages: list = []
    __current_page: int = 0
    __title: str = ""
    __color: int = 0x75E6DA
     
    def __init__(self, pages: list, title: str, color: int = 0x75E6DA) -> None:
        super().__init__()
        if len(pages) == 0:
            self.__pages = [""]
        else:
            self.__pages = pages
            
        self.__title = title
        self.__color = color
        
    @property
    def current_page(self) -> int:
        return self.__current_page 
    
    @current_page.setter
    def current_page(self, value: int) -> None:
        if value < len(self.__pages) and value >= 0:
            self.__current_page = value
        print(self.__current_page)

    
    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="⬅") 
    async def left_callback(self, button, interaction):
        self.current_page -= 1
        await self.__refresh(interaction)
        
    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="➡")
    async def right_callback(self, button, interaction):
        self.current_page += 1
        await self.__refresh(interaction)
        
    async def __refresh(self, interaction) -> None:
        await interaction.response.edit_message(embed = self.embeb)
        
    @property
    def embeb(self) -> discord.Embed:
        embed = discord.Embed(title=self.__title, description=self.__pages[self.current_page], color=self.__color)
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.__pages)}")
        return embed