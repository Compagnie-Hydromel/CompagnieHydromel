import random
import discord
from scheduler.asyncio import Scheduler
import datetime
import asyncio

from libs.config import Config
from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.utils.utils import Utils


class ScheduledTask(discord.Cog):
    __bot: discord.bot.Bot
    __schedule: Scheduler

    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()

    @discord.Cog.listener()
    async def on_ready(self):
        loop = asyncio.get_running_loop()
        self.__schedule = Scheduler(loop=loop)

        self.__schedule.daily(timing=datetime.time(
            16, 16), handle=self.monthly_top_adder)

        while True:
            await asyncio.sleep(1)

    async def monthly_top_adder(self):
        # if datetime.date.today().day != 1:
        #     return

        for guild in Guild.all():
            most_active_users: list[GuildUser] = guild.get_monthly_top_users()
            most_active_reward: list[int] = [70, 50, 30, 5, 3]

            for user, i in zip(most_active_users, range(len(most_active_users))):
                user.point += most_active_reward[i]
                user.smartpoint += most_active_reward[i]
                user.save()

            monthlytop_channel_id = int(guild.monthlytop_channel_id)
            if monthlytop_channel_id == 0:
                continue

            information_channel = self.__bot.get_channel(monthlytop_channel_id)

            if information_channel is not None:
                embed = discord.Embed(title="Monthly Top Users", color=eval(
                    "0x" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])))

                for user in most_active_users:
                    username = Utils.get_user_name_or_id_by_discord_id(
                        user.user.discord_id, self.__bot)
                    embed.add_field(
                        name=username, value=user.monthly_point, inline=False)

                await information_channel.send(embed=embed)

            for user in guild.guildusers:
                user.monthly_point = 0
                user.save()


def setup(bot: discord.bot.Bot):
    bot.add_cog(ScheduledTask(bot))
