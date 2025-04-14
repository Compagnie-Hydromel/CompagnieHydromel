import random
import discord
from scheduler.asyncio import Scheduler
import datetime
import asyncio

from libs.config import Config
from libs.databases.model.user.user import User
from libs.databases.model.user.users import Users
from libs.utils.utils import Utils


class ScheduledTask(discord.Cog):
    __bot: discord.bot.Bot
    __schedule: Scheduler

    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__users = Users()
        self.__config = Config()

    @discord.Cog.listener()
    async def on_ready(self):
        loop = asyncio.get_running_loop()
        self.__schedule = Scheduler(loop=loop)

        self.__schedule.daily(timing=datetime.time(
            14, 17), handle=self.monthly_top_adder)

        while True:
            await asyncio.sleep(1)

    async def monthly_top_adder(self):
        if datetime.date.today().day != 1:
            return

        most_active_users: list[User] = self.__users.get_5_monthly_most_active_users
        most_active_reward: list[int] = [70, 50, 30, 5, 3]

        for user, i in zip(most_active_users, range(len(most_active_users))):
            user.add_point(most_active_reward[i])
            user.add_smartpoint(most_active_reward[i])

        information_channel = self.__bot.get_channel(
            self.__config.value["monthlytop_channel_id"])

        if information_channel is not None:
            embed = discord.Embed(title="Monthly Top Users", color=eval(
                "0x" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])))

            for user in most_active_users:
                username = Utils.get_user_name_or_id_by_discord_id(
                    user.discord_id, self.__bot)
                embed.add_field(
                    name=username, value=user.monthly_point, inline=False)

            await information_channel.send(embed=embed)

        for user in self.__users.all:
            user.reset_monthly_point()


def setup(bot: discord.bot.Bot):
    bot.add_cog(ScheduledTask(bot))
