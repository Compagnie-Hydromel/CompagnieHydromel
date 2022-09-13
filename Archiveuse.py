#!/usr/bin/python3

#-----------------------------
# Name : Archiveuse
# Author : Ethann Schneider
# Version : 2.3.3
# Date : 20.08.22
#-----------------------------

import discord
from discord.ext import tasks
import datetime
import os
import re
import random
from base64 import b64encode, b64decode
import hashlib
import json
import praw
import lib.imageMaker as imageMaker
from lib.user import *
from io import BytesIO
import requests
import lib.commands as commands

BotId = 3

TOKEN = None
if os.path.exists("key.txt"):
    with open("key.txt", "r") as key:
        TOKEN = key.readline()
else:
    TOKEN = commands.getBotInfo(BotId)[1]

intents = discord.Intents.default()
intents.members = True

global root, option

client = discord.Client(intents=intents)

def reload():
    global root, rootoptions, options
    root = commands.getAllRoot()
    rootoptions = commands.getCommands(BotId, True)
    options = commands.getCommands(BotId)

def wallpaperList(id, wallpapers=getAllWallpaper(), page=1):
    global embed
    embed=discord.Embed(title="Wallpaper", description="page "+str(page), color=0x6D071A)

    y = 0

    for i in wallpapers:
        if y > 10*page-11 and y < page*11:
            if i in getUserBuyWallpaper(str(id)):
                embed.add_field(name="*"+i+"*", value="obtenu", inline=False)
            else:
                if wallpapers[i]['price'] != 0:
                    embed.add_field(name=i, value="prix : " + str(wallpapers[i]['price']), inline=False)
                elif wallpapers[i]['level'] != 0:
                    embed.add_field(name=i, value="niveaux : " + str(wallpapers[i]['level']), inline=False)
                else:
                    embed.add_field(name=i, value="Aucun level et prix", inline=False)
        y+=1

    return embed

async def balance(message,argument):
    await message.channel.send("Balance : "+str(getBalance(message.author.id)))

async def showChangeWallpaper(message,argument):
    if argument[1] in getUserBuyWallpaper(str(message.author.id)):
        changeWallpaper(message.author.id, argument[1])
        await message.channel.send("Wallpaper modifié")
    elif argument[1] in getAllWallpaper():
        await message.channel.send("Wallpaper pas obtenu par contre petite apercu", file=discord.File("img/wallpaper/"+argument[1], filename=argument[1]+".jpg"))
    else:
        pages = 1
        if argument[1].isnumeric():
            pages = int(argument[1])

        await message.channel.send(embed=wallpaperList(message.author.id, page=pages))

async def showBuyWallpaper(message,argument):
    if argument[1] in getAllWallpaper():
        if argument[1] not in getUserBuyWallpaper(str(message.author.id)):
            wallpaper = getWallpaper(argument[1])
            if wallpaper[2] != 0:
                if removeBalance(str(message.author.id), wallpaper[2]):
                    buyWallpaper(message.author.id, argument[1])
                    await message.channel.send("Wallpaper acheté")
                else:
                    await message.channel.send("Pas assez de money")
            else:
                await message.channel.send("Pas achetable peut seulement s'obtenir avec des niveaux")
        else:
            await message.channel.send("Déjà acheté")
    else:
        pages = 1
        if argument[1].isnumeric():
            pages = int(argument[1])

        await message.channel.send(embed=wallpaperList(message.author.id, page=pages))

async def showYourWallpaper(message,argument):
    pages = 1
    if argument[1].isnumeric():
        pages = int(argument[1])

    await message.channel.send(embed=wallpaperList(message.author.id, page=pages, wallpapers=getUserBuyWallpaper(message.author.id)))

async def show(message,argument):
    if argument[0] == "wallpaper":
        await showChangeWallpaper(message,argument)
    elif argument[0] == "yourWallpaper":
        await showYourWallpaper(message,argument)
    elif argument[0] == "buy":
        await showBuyWallpaper(message,argument)
    elif argument[0] == "barColor":
        await changeBarColor(message,argument)
    elif argument[0] == "nameColor":
        await changeNameColor(message,argument)
    else:
        id = message.author.id
        url = ""
        if message.author.avatar != None:
            url = "https://cdn.discordapp.com/avatars/"+str(id)+"/"+message.author.avatar+".png"
        else:
            url = "https://shkermit.ch/Shkermit.png"

        userInfo = getUserInfo(id)

        if not os.path.exists("img/profil/"):
            os.makedirs("img/profil/")
        await message.channel.send("", file=discord.File(imageMaker.createProfil("img/profil/"+str(id)+".png", str(message.author), url, userInfo[0], userInfo[1], message.author.display_name, getBadgeList(id), userInfo[2])))

async def money(message,argument):
    getUserID = re.findall(r'^<@(\S+)>$',argument[1])
    if getUserID:
        if client.get_user(int(getUserID[0])) != None:
            if argument[0] == "add":
                if argument[2].isnumeric():
                    addUserIfNotExist(str(getUserID[0]))
                    addBalance(getUserID[0], argument[2])
                    await message.channel.send("Now current balance of "+client.get_user(int(getUserID[0])).name+" is "+str(getBalance(getUserID[0])))
                else:
                    await message.channel.send("Please use number to add")
            elif argument[0] == "remove":
                if argument[2].isnumeric():
                    addUserIfNotExist(str(getUserID[0]))
                    if removeBalance(getUserID[0], argument[2]):
                        await message.channel.send("Now current balance of "+client.get_user(int(getUserID[0])).name+" is "+str(getBalance(getUserID[0])))
                    else:
                        await message.channel.send("To much money to remove")

                else:
                    await message.channel.send("Please use number to remove")
            elif argument[0] == "show":
                await message.channel.send(client.get_user(int(getUserID[0])).name+" as "+str(getBalance(getUserID[0]))+" money")

            else:
                await message.channel.send("Usage : !money <add/remove/show> <@someone> <number>")

        else:
            await message.channel.send("Please use a real user")
    else:
        await message.channel.send("Usage : !money <add/remove/show> <@someone> <number>")

async def manageWallpaper(message,argument):
    if argument[0] == "add":
        if len(message.attachments) > 0 and argument[1] != '':
            response = requests.get(message.attachments[0].url)
            open("img/wallpaper/"+argument[1], "wb").write(response.content)
            if argument[2] in ("level", "price") and argument[3].isnumeric():
                addWallpaper(argument[1], argument[2], argument[3])
            else:
                addWallpaper(argument[1], "price", random.randint(5,20)*100)
            await message.channel.send("Wallpaper added")
        else:
            await message.channel.send("No image in attachments and argument 2 need to be name of the wallpaper")
    if argument[0] == "remove":
        if removeWallpaper(argument[1]):
            await message.channel.send("Wallpaper removed")
        else:
            await message.channel.send("Wallpaper does not exist")



@tasks.loop(seconds = 290)
async def loopVocalPoint():
    servers = client.guilds
    for server in servers:
        channels = server.channels
        for channel in channels:
            if isinstance(channel, discord.VoiceChannel):
                members = channel.members
                for member in members:
                    if not member.voice.self_deaf:
                        if len(members) == 1 and random.randint(0,3) != 2:
                            return
                        addUserIfNotExist(str(member.id))
                        addPoint(str(member.id))


root = []
rootoptions = {}
options = {}

@client.event
async def on_message(message):
    print("(in "+str(message.channel)+" at "+str(datetime.datetime.now())+")"+str(message.author)+": "+message.content)
    if message.author == client.user:
        return

    addUserIfNotExist(str(message.author.id))

    if not isinstance(message.channel, discord.channel.DMChannel):
        if addPoint(str(message.author.id)):
            await message.author.send("Bravo tu es passé niveau "+str(getUserInfo(str(message.author.id))[0]))

    commands=re.findall(r'^!(\S+)((\s+(\S+))?)+$',message.content)
    if commands:
        argument = re.split(' |\n',message.content[len(commands[0][0])+2:])
        for i in range(1,10):
            argument.append("")

        reload()
        if commands[0][0] in rootoptions:
            if str(message.author.id) in root:
                await eval(rootoptions[commands[0][0]]['cmd'])

        if commands[0][0] in options:
            if options[commands[0][0]]['perm'] == True:
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
    loopVocalPoint.start()


client.run(TOKEN)
