from io import BytesIO
import traceback
import discord
from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.profile_layout import ProfileLayout

from libs.databases.models.wallpaper import Wallpaper
from libs.exception.handler import Handler
from libs.log import Log
from libs.paginator import Paginator
from libs.storages.storage import Storage


class ProfileManager(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()
        self.storage = Storage()

    @discord.slash_command(description="Manage your profile")
    @discord.option("option", description="list/change", choices=["set wallpaper", "buy wallpaper", "list of posseded wallpaper", "all wallpaper", "wallpaper preview", "name color", "bar color", "list profile layout", "change profile layout"])
    @discord.option("options_specifies", description="Specifies wallpaper or name color and bar color", required=False)
    async def profile_manager(self, ctx: discord.commands.context.ApplicationContext, *, option: str, options_specifies: str = ""):
        Log.command(ctx.author.name + " is launching wallpaper commands with " +
                    option + " " + str(options_specifies))
        try:
            await ctx.defer()

            if not ctx.guild:
                return await ctx.respond("Command can only be used in a server.")

            user = GuildUser.from_user_discord_id_and_guild_discord_id(
                ctx.author.id, ctx.guild.id)
            guild = Guild.from_discord_id(ctx.guild.id)

            match option:
                case "set wallpaper":
                    wallpaper = Wallpaper.from_name(options_specifies)
                    if wallpaper is None:
                        wallpaper = Wallpaper.default()
                        options_specifies = "default wallpaper"
                    user.wallpaper = wallpaper
                    wallpaper.saveOrFail()
                    await ctx.respond("Wallpaper set to " + options_specifies)
                case "buy wallpaper":
                    wallpaper = Wallpaper.from_name(options_specifies)
                    user.smartpoint -= wallpaper.price
                    user.saveOrFail()
                    user.wallpapers.append(wallpaper)
                    await ctx.respond("Wallpaper " + wallpaper.name + " bought")
                case "list of posseded wallpaper":
                    await self.__respond_list(ctx, user.wallpapers, "Posseded wallpapers")
                case "all wallpaper":
                    await self.__respond_list(ctx, guild.wallpapers, "All wallpapers")
                case "wallpaper preview":
                    wallpaper = Wallpaper.from_name(options_specifies)
                    if wallpaper is None:
                        return await ctx.respond("Wallpaper not found")
                    filename = self.storage.get_file_type(wallpaper.url)
                    await ctx.respond(file=discord.File(self.storage.get(wallpaper.url, return_type=BytesIO), filename="preview." + filename))
                case "name color":
                    user.name_color = options_specifies
                    user.saveOrFail()
                    await ctx.respond("Name color changed to " + options_specifies)
                case "bar color":
                    user.bar_color = options_specifies
                    user.saveOrFail()
                    await ctx.respond("Bar color changed to " + options_specifies)
                case "list profile layout":
                    await self.__respond_list(ctx, ProfileLayout.all(), "Profile layout")
                case "change profile layout":
                    user.profileLayout = ProfileLayout.from_name(
                        options_specifies)
                    await ctx.respond("Profile layout changed to " + options_specifies)
                case _:
                    await ctx.respond("Invalid option. Please choose a valid profile management option.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    async def __respond_list(self, ctx: discord.commands.context.ApplicationContext, list: list, page_name: str = "Wallpapers"):
        paginator = Paginator(self.__generate_pages(list), page_name, 0x75E6DA)

        await ctx.respond(
            view=paginator,
            embed=paginator.embed
        )

    def __generate_pages(self, list_of_line: list[any]) -> list:
        pages = []
        line_per_page = 10
        counter = 0
        content = ""

        for line in list_of_line:
            if isinstance(line, Wallpaper):
                content += self.wallpaper_list_with_price(line)
            elif isinstance(line, ProfileLayout):
                content += line.name + "\n"
            counter += 1

            if counter > line_per_page:
                pages.append(content)
                content = ""
                counter = 0
        if content != "":
            pages.append(content)
        return pages

    def wallpaper_list_with_price(self, wallpaper: Wallpaper):
        unlock_with = ""
        if wallpaper.price != 0:
            unlock_with += "\n" + str(wallpaper.price) + " smartpoint"
        elif wallpaper.level != 0:
            unlock_with += "\nUnlock at level " + str(wallpaper.level)
        else:
            unlock_with += "\n" + "not buyable"

        return "**" + str(wallpaper.name) + "**" + unlock_with + "\n"


def setup(bot: discord.bot.Bot):
    bot.add_cog(ProfileManager(bot))
