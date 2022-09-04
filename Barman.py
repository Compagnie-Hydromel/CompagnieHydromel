#!/usr/bin/python3

#-----------------------------
# Name : George le barman
# Author : Ethann Schneider
# Version : 1.7.1
# Date : 09.04.22
#-----------------------------

import discord
import datetime
import os
import re
import random
from base64 import b64encode, b64decode
import hashlib
import json
import praw
import lib.imageMaker as imageMaker
import lib.commands as commands

global options, rootoptions, root

BotId = 1

TOKEN = None
if os.path.exists("key.txt"):
    with open("key.txt", "r") as key:
        TOKEN = key.readline()
else:
    TOKEN = commands.getBotInfo(BotId)[1]

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

reddit = praw.Reddit(client_id='yyUCyKBxIWjKESgtOhlaBg',
                     client_secret='bM5hG8gkzMokN2MvG_sTsP-g3OfuIg',
                     user_agent='lol', check_for_async=False)

def permsForHelp(command):
    text = ""
    if options[command]['perm']:
        for i in options[command]['perm']:
            if i != 'dm':
                text += client.get_channel(i).name + " "
            else:
                text += "Private Message "

    return text

def getImageReddit(redditName):
    memes_submissions = reddit.subreddit(redditName).hot()
    post_to_pick = random.randint(1, 100)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submissions if not x.stickied)

    return submission

async def help(message,argument):
    embed = None;

    if argument[0] in options and not options[argument[0]]['hide']:
        embed=discord.Embed(title="!"+argument[0], description=options[argument[0]]['description']+"\nChannel: "+permsForHelp(argument[0]), color=0x6D071A)

    elif argument[0] in rootoptions:
        if message.author.id in root:
            embed=discord.Embed(title="!"+argument[0], description=rootoptions[argument[0]]['description'], color=0x6D071A)

    else:
        embed=discord.Embed(title="List Command Help", color=0x6D071A)

        for i in options:
            if not options[i]['hide']:
                embed.add_field(name="!"+i, value=options[i]['description']+"\nChannel: "+permsForHelp(i), inline=False)

    await message.channel.send(embed=embed)

async def caveDeTorture(message, argument):
    if hashlib.sha256(bytes(argument[0], 'utf-8')).hexdigest() == 'b33aa8cb667db7f7af0c6f8aeba093086a6e2679bdc0da14048a44a5404b1700':
        await client.get_channel(928305361797144618).set_permissions(message.author, view_channel=True, read_message_history=True, send_messages=True, read_messages=True)
        await message.channel.send("Salon ajouté correctement")
    else:
        await message.channel.send('''Avant que je te révéle le mot de passe tu dois savoir que les images pourrait voir vont te choquer (image gore, sex, sang, ect...) et tu ne dois pas prendre cette avertissement a la légére c'est pour cela que je vais donner le mot de passe sous forme "crypté". voilà le base64 du mot de passe : "amVTdWlzUmVzcG9uc2FibGVEZU1hUHJvcHJlU2FudGVNZW50YWxl"''')

async def SendMessage(message, argument, messages, files=None):
    if files == None:
        await message.channel.send(messages)
    elif os.path.isdir(files):
        list = os.listdir(files)
        await message.channel.send(file=discord.File(files+"/"+list[random.randint(0,len(list))-1]))
    else:
        await message.channel.send(messages, file=discord.File(files))

def get_voice_channel(id,guild_id=928279859627696179):
    guild = client.get_guild(guild_id)
    channels = guild.channels
    for i in channels:
        if isinstance(i, discord.VoiceChannel) and i.id == id:
            return i
    return None

def getBarImage():
    coords = {
        'bar': {"w":390,"h":215, "id": 928302763551645696},
        'table1': {"w":110,"h":279, "id": 928302830463377418},
        'table2': {"w":607,"h":293, "id": 928303177831432255},
        'table3': {"w":450,"h":457, "id": 928351848811888690}
    }
    people = {}

    for coord in coords:
        people[coord] = []
        vocal = get_voice_channel(coords[coord]["id"])
        for member in vocal.members:
            url = "https://cdn.discordapp.com/avatars/"+str(member.id)+"/"+member.avatar+".png"
            people[coord].append({"username": member.name, "profil": url })

    return imageMaker.createBar('.taverne.png' ,'img/taverne.jpg', coords, people)

async def quit(message,argument):
    await message.channel.send("bye, bye")
    await client.close()

async def clear(message,argument):
    if not isinstance(message.channel, discord.channel.DMChannel):
        await message.channel.purge()

async def reload(message,argument):
    rootoptions = commands.getCommands(BotId, True)
    options = commands.getCommands(BotId)
    root = commands.getAllRoot()
    await message.channel.send("reloaded")

async def broadcast(message,argument):
    message = ""
    channel = None
    for i in argument[1:]:
        message+=str(i)+" "

    if argument[0].isnumeric():
        channel = client.get_channel(int(argument[0]))

    if channel != None:
        await channel.send(message)

async def channel(message,argument):
    listAllCommands = commands.getCommands(BotId, all=True)
    if argument[1] in listAllCommands:
        if argument[0] == 'add':
            if isinstance(message.channel, discord.channel.DMChannel):
                commands.setDmAccess(argument[1])
            else:
                pass
            await message.channel.send("Salon ajouté")
        elif argument[0] == 'remove':
            await message.channel.send("Salon retiré")
    else:
        await message.channel.send("commands inexistante")

async def rootManage(message,argument):
    global root
    getUserID = re.findall(r'^<@(\S+)>$',argument[1])
    if (argument[0] == 'add' or argument[0] == 'remove') and getUserID:
        newRoot = client.get_user(int(getUserID[0]))

        if argument[0] == 'add':
            commands.setRoot(getUserID[0],True)
        else:
            commands.setRoot(getUserID[0],False)

        root = commands.getAllRoot()
        await message.channel.send(str(newRoot)+" "+argument[0])
    elif argument[0] == 'list':
        embed=discord.Embed(title="Root", color=0x138EC3)

        for i in root:
            embed.add_field(name=client.get_user(int(i)), value=i, inline=False)

        await message.channel.send(embed=embed)
    else:
        await message.channel.send("Usage : !root (add/remove/list) (@someone)")

rootoptions = commands.getCommands(BotId, True)

options = commands.getCommands(BotId)
# {
#   "help":{"cmd":"help", "description":"Simple Help page", "perm":["dm",928452291500048434], "hide":false},
#   "verre":{"cmd":"verre", "description":"Pour te servir un beau verre", "perm":[928452291500048434], "hide":false},
#   "biere":{"cmd":"verre", "description":"Pour te servir une belle bière", "perm":[928452291500048434], "hide":false},
#   "beer":{"cmd":"verre", "description":"Pour te servir une belle bière", "perm":[928452291500048434], "hide":false},
#   "hydromel":{"cmd":"hydromel", "description":"Pour te servir un verre d'hydromel", "perm":[928452291500048434], "hide":false},
#   "water":{"cmd":"water", "description":"Pour te servir un verre d'eau pour les faibles", "perm":[928452291500048434], "hide":false},
#   "verresansalcool":{"cmd":"verreSansAlcool", "description":"Pour te servir un verre sans alcool de faible", "perm":[928452291500048434], "hide":false},
#   "caveDeTorture":{"cmd":"caveDeTorture", "description":"...", "perm":["dm"], "hide":true},
#   "hentai":{"cmd":"hentai", "description":"Pour avoir des photos de hentai", "perm":["dm",952930745465307156], "hide":false},
#   "porn":{"cmd":"porn", "description":"Pour avoir des photos pornographiques", "perm":["dm",952930745465307156], "hide":false},
#   "jinx":{"cmd":"jinx", "description":"Pour avoir des photos de Jinx ;)", "perm":["dm",952930745465307156], "hide":false},
#   "002":{"cmd":"ZeroTwo", "description":"Pour avoir des photos Zero Two", "perm":["dm",952930745465307156], "hide":false},
#   "shitpost":{"cmd":"shitpost", "description":"Pour envoyer du shitpost", "perm":["dm",952930745465307156,928305986484195329], "hide":false}
# }


root = commands.getAllRoot()

@client.event
async def on_message(message):
    log = "(in "+str(message.channel)+" at "+str(datetime.datetime.now())+")"+str(message.author)+": "+message.content
    with open("log.txt", "a") as f:
        f.write(log+"\n")
    print(log)
    if message.author == client.user:
        return

    if message.type == discord.MessageType.premium_guild_subscription:
        if message.guild.id == 928279859627696179:
            await client.get_channel(978604995563888664).send(message.author.mention+" vient de booster le serveur ce BG !")

    commands=re.findall(r'^!(\S+)((\s+(\S+))?)+$',message.content)
    if commands:
        argument = re.split(' |\n',message.content[len(commands[0][0])+2:])
        for i in range(1,10):
            argument.append("")
        if commands[0][0] in rootoptions:
            if str(message.author.id) in root:
                await eval(rootoptions[commands[0][0]]['cmd'])

        if commands[0][0] in options:
            if not options[commands[0][0]]['perm']:
                await eval(options[commands[0][0]]['cmd'])
            elif 'dm' in options[commands[0][0]]['perm'] and isinstance(message.channel, discord.channel.DMChannel):
                await eval(options[commands[0][0]]['cmd'])
            elif message.channel.id in options[commands[0][0]]['perm']:
                await eval(options[commands[0][0]]['cmd'])

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user)
    print(client.user.id)
    print('------')

# Join Leave

@client.event
async def on_voice_state_update(members, before, after):
    with open(getBarImage(), "rb") as image:
        await client.get_guild(928279859627696179).edit(banner=image.read())

# reaction --

@client.event
async def on_raw_reaction_add(reaction):
                                           #messages id        channel id          emoji        guild/server id     role_id
    await add_role_with_reaction(reaction, 928440687538614292, 928302162663047258, "✅"         ,928279859627696179, 928310296584532000) # membre
    await add_role_with_reaction(reaction, 928444580964229130, 928302543447130164, "panneau"   ,928279859627696179, 928309020182319146) # panneau
    await add_role_with_reaction(reaction, 928444580964229130, 928302543447130164, "damnation" ,928279859627696179, 928311769800269844) # damnation

@client.event
async def on_raw_reaction_remove(reaction):
                                              #messages id        channel id          emoji        guild/server id     role_id
    await remove_role_with_reaction(reaction, 928440687538614292, 928302162663047258, "✅"         ,928279859627696179, 928310296584532000) # membre
    await remove_role_with_reaction(reaction, 928444580964229130, 928302543447130164, "panneau"   ,928279859627696179, 928309020182319146) # panneau
    await remove_role_with_reaction(reaction, 928444580964229130, 928302543447130164, "damnation" ,928279859627696179, 928311769800269844) # damnation


# reaction add
async def add_role_with_reaction(reaction, message_id, channel_id, emoji, guild_id, role_id):
    if(reaction.message_id == message_id and reaction.channel_id == channel_id and reaction.emoji.name == emoji and reaction.guild_id == guild_id):
        role = discord.utils.get(reaction.member.guild.roles, id=role_id)
        await reaction.member.add_roles(role)

async def remove_role_with_reaction(reaction, message_id, channel_id, emoji, guild_id, role_id):
    member = client.get_user(reaction.user_id)
    guild = client.get_guild(reaction.guild_id)
    if(reaction.message_id == message_id and reaction.channel_id == channel_id and reaction.emoji.name == emoji and reaction.guild_id == guild_id):
        role = discord.utils.get(guild.roles, id=role_id)
        member2 = discord.utils.get(guild.members, id=reaction.user_id)
        await member2.remove_roles(role)

# end reaction

client.run(TOKEN)
