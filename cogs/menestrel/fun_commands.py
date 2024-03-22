import os
import traceback
import discord
import random
import praw
from blagues_api import BlaguesAPI
from dotenv import load_dotenv
from libs.config import Config
from libs.exception.handler import Handler

from libs.log import Log

load_dotenv()

class FunCommands(discord.Cog):
    def __init__(self, bot) -> None:
        self.___bot = bot
        self.__error_handler = Handler()
                
    @discord.slash_command(description="Command to play *Rock, Paper, Scissors*.")
    @discord.option(name="choice", choices=["Rock", "Paper", "Scissors"])
    async def rock_paper_scissors(self, ctx : discord.ApplicationContext, choice : str):
        Log.command(ctx.author.name + " is launching rock_paper_scissors commands")
        try: 
            possibilities = ["Rock", "Paper", "Scissors"]
            possibilities_emojis = [":rock:", ":page_facing_up:", ":scissors:"]
            random_choice = random.choice(possibilities)
            
            if choice == random_choice:
                winner_id = -1
            elif random_choice == possibilities[0]:
                if choice == possibilities[2]:
                    winner_id = ctx.bot.user.id
                else:
                    winner_id = ctx.author.id
            elif random_choice == possibilities[1]:
                if choice == possibilities[0]:
                    winner_id = ctx.bot.user.id
                else:
                    winner_id = ctx.author.id
            elif random_choice == possibilities[2]:
                if choice == possibilities[1]:
                    winner_id = ctx.bot.user.id
                else:
                    winner_id = ctx.author.id
                
            bot_choice_emoji = possibilities_emojis[possibilities.index(random_choice)]
            user_choice_emoji = possibilities_emojis[possibilities.index(choice)]
            
            message = f"{bot_choice_emoji} (<@{ctx.bot.user.id}>) X {user_choice_emoji} (<@{ctx.author.id}>)\n\n"
            
            if winner_id == -1: message += "Egalité !"
            else: message += f"Winner is <@{winner_id}> :trophy: !"
            
            await ctx.respond(message)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
        
    @discord.slash_command(description="Get a random joke")
    @discord.option(name="type",choices=["Global", "Dev", "Beauf"])
    async def joke(self, ctx : discord.ApplicationContext, type : str):
        Log.command(ctx.author.name + " is launching joke commands")
        try:
            if os.getenv("BLAGUES_API_KEY") is None:
                await ctx.respond("Not api access!")
                return

            blagues = BlaguesAPI(os.getenv("BLAGUES_API_KEY"))
            
            blague = await blagues.random_categorized(type.lower())
            
            blague_infos = [blague.joke, blague.answer]
            
            await ctx.respond(f"{blague_infos[0]}\n\n\n{blague_infos[1]}")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
        
    @discord.slash_command(name="meme", description="Get a random meme from reddit")
    async def meme(self, ctx : discord.ApplicationContext):
        Log.command(ctx.author.name + " is launching meme commands")
        try:
            await ctx.defer()
            
            if os.getenv("REDDIT_CLIENT_ID") is None and os.getenv("REDDIT_CLIENT_SECRET") is None:
                await ctx.respond("Not api access!")
                return
            reddit = praw.Reddit(
                client_id = os.getenv("REDDIT_CLIENT_ID"),
                client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent = 'lol', 
                check_for_async = False
            )
            
            memes_submissions = reddit.subreddit("meme").hot()
            post_to_pick = random.randint(1, 100)
            for i in range(0, post_to_pick):
                submission = next(x for x in memes_submissions if not x.stickied)

            await ctx.respond(submission.url)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            
    
def setup(bot):
    bot.add_cog(FunCommands(bot))