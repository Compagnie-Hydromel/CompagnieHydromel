import discord


class Paginator(discord.ui.View):
    """This class is designed to make a paginator.
    """
    __pages: list = []
    __current_page: int = 0
    __title: str = ""
    __color: int = 0x75E6DA

    def __init__(self, pages: list[str], title: str, color: int = 0x000000) -> None:
        """This method is designed to initialize the Paginator class.

        Args:
            pages (list[str]): The page to display.
            title (str): The title of the paginator.
            color (int, optional): The color of the embed. Defaults to 0x75E6DA.
        """
        super().__init__()
        if len(pages) == 0:
            self.__pages = [""]
        else:
            self.__pages = pages

        self.__title = title
        self.__color = color

    @property
    def current_page(self) -> int:
        """This method is designed to get the current page.

        Returns:
            int: The current page.
        """
        return self.__current_page

    @current_page.setter
    def current_page(self, value: int) -> None:
        """This method is designed to set the current page.

        Args:
            value (int): The new current page.
        """
        if value < len(self.__pages) and value >= 0:
            self.__current_page = value

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="⬅")
    async def left_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        """This method is a callback designed to go to the left page.

        Args:
            button (discord.ui.Button): The button that was clicked.
            interaction (discord.interactions.Interaction): The discord interaction.
        """
        self.current_page -= 1
        await self.__refresh(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="➡")
    async def right_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction) -> None:
        """This method is a callback designed to go to the right page.

        Args:
            button (discord.ui.Button): The button that was clicked.
            interaction (discord.interactions.Interaction): The discord interaction.
        """
        self.current_page += 1
        await self.__refresh(interaction)

    async def __refresh(self, interaction: discord.interactions.Interaction) -> None:
        """This method is designed to refresh the paginator.

        Args:
            interaction (discord.interactions.Interaction): The discord interaction.
        """
        await interaction.response.edit_message(embed=self.embed)

    @property
    def embed(self) -> discord.Embed:
        """This method is designed to get the embed.

        Returns:
            discord.Embed: The embed.
        """
        embed = discord.Embed(
            title=self.__title, description=self.__pages[self.current_page], color=self.__color)
        embed.set_footer(
            text=f"Page {self.current_page + 1}/{len(self.__pages)}")
        return embed
