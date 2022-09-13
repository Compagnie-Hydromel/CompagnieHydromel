#!/usr/bin/python3

#-----------------------------
# Name : George le barman
# Author : Ethann Schneider
# Version : 2.0.1
# Date : 03.07.22
#-----------------------------

import discord
import datetime
import os
import re
import json
import yt_dlp
from urllib.parse import urlparse, parse_qs
from contextlib import suppress
from discord.ext import tasks
import asyncio
from youtube_search import YoutubeSearch
import lib.commands as commands
import lib.bot as bot

BotId = 2

TOKEN = None
if os.path.exists("key.txt"):
    with open("key.txt", "r") as key:
        TOKEN = key.readline()
else:
    TOKEN = bot.getBotInfo(BotId)[1]

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

global vc, queue

vc = {}
lock = {}
queue = {}

def reload():
    global root, rootoptions, options
    root = commands.getAllRoot()
    rootoptions = commands.getCommands(BotId, True)
    options = commands.getCommands(BotId)

# Music function

'''
@Name join Channel
@Description To made bot join Vocal Channel where user is
@args1 Message Message that was send by User
@return Null
'''
def joinChannel(message):
    return message.author.voice.channel.connect()

'''
@Name play Music
@Description play Music with path or add it to the queue
@args1 path Path To File
@args2 voc Vocal where to play
@args3 id server id
@return bool return true if played false if added to queue
'''
def playMusic(path, voc, id):
    if not voc.is_playing():
        try:
            voc.play(discord.FFmpegPCMAudio(path), after=lambda e: asyncio.run_coroutine_threadsafe(nextMusicOrQuit(voc, id), client.loop))
            return True
        except:
            vc[message.guild.id] = None
            return False
    else:
        return False

'''
@Name next Music Or Quit
@Description play next music in queue or quit
@args1 voc Vocal where to play
@args2 id server id
@return text to send in chat
'''
async def nextMusicOrQuit(voc, id):
    if not voc.is_playing():
        if not nextMusic(voc, id):
            await voc.disconnect()

            if id in vc:
                vc[id] = None
            if id in queue:
                queue[message.guild.id] = []

'''
@Name next Music
@Description play next music in queue
@args1 voc Vocal where to play
@args2 id server id
@return bool
'''
def nextMusic(voc, id):
    if id in queue:
        if len(queue[id]) > 0:
            if voc.is_playing():
                voc.stop()

            playMusic(queue[id].pop(), voc, id)

            return True
        else:
            return False

'''
@Name get youtube id
@Description get youtube id with url
@link https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
@args1 url
@args2 ignore_playlist=False If ignore playlist
@return id of video
'''
def get_yt_id(url, ignore_playlist=True):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
        # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]

'''
@Name youtube Download
@Description Dowload Video with link
@args1 ytb Link
@return Null
'''
def youtubeDwl(ytb, cachePath="music"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': cachePath+'/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(ytb)

'''
@Name search Youtube
@Description return youtube id of the search
@args1 str search string
@return str of the youtube id
'''
def searchYoutube(searched):
    return YoutubeSearch(searched, max_results=1).to_dict()[0]["id"]

def musicCachePath():
    try:
        with open("musicCachePath", "r") as f:
            return str(f.readlines(0)[0].replace("\n", ""))
    except Exception as e:
        return "music"

# Music function

# Music commands

'''
@Name Play
@Description Command play to play music in vocal
@args1 message message that was sent by user
@args2 argument argument of the commands
@return Null
'''
async def play(message,argument):
    global vc, queue
    if not isinstance(message.channel, discord.channel.DMChannel):
        if message.guild.id not in lock:
            lock[message.guild.id] = False

        if message.guild.id not in vc:
            vc[message.guild.id] = None

        if lock[message.guild.id] and str(message.author.id) not in root:
            await message.channel.send("Sorry i can't")
            return

        try:
            SearchedMusic = ""
            fileName = ""
            ytId = ""
            cachePath = musicCachePath()
            if 'youtu.be' in argument[0] or 'youtube.com' in argument[0]:
                fileName = cachePath+"/"+get_yt_id(argument[0])+".mp3"
                ytId = get_yt_id(argument[0])
            else:
                for arg in argument:
                    SearchedMusic = SearchedMusic + " " + arg
                if SearchedMusic.replace(" ", "") == "":
                    SearchedMusic = "Ethann saga"
                ytId = searchYoutube(SearchedMusic)
                fileName = cachePath+"/"+str(ytId)+".mp3"

            if not os.path.exists(fileName):
                if not os.path.exists(cachePath):
                    os.mkdir(cachePath)
                youtubeDwl("https://www.youtube.com/watch?v="+str(ytId), cachePath)

            if vc[message.guild.id] == None:
                vc[message.guild.id] = await joinChannel(message)

            if playMusic(fileName, vc[message.guild.id], message.guild.id):
                await message.channel.send("Playing")
            else:
                if message.guild.id not in queue:
                    queue[message.guild.id] = []
                queue[message.guild.id].insert(0, fileName)
                await message.channel.send("Added in queue")
        except Exception as e:
            await message.channel.send("Erreur technique vérifier que se soit une video téléchargeable ou que vous soyez dans un salon vocaux")
            print(e)

'''
@Name Stop
@Description Command stop to stop music in vocal
@args1 message Message that was sent by user
@args2 argument argument of the commands
@return Null
'''
async def stop(message,argument):
    global vc, queue

    if not isinstance(message.channel, discord.channel.DMChannel):
        if message.guild.id not in lock:
            lock[message.guild.id] = False

        if lock[message.guild.id] and message.author.id not in root:
            await message.channel.send("Sorry i can't")
            return

        if vc[message.guild.id] != None:
            await vc[message.guild.id].disconnect()

            if id in vc:
                vc[message.guild.id] = None
            if id in queue:
                queue[message.guild.id] = []

            await message.channel.send("Stopping")
        else:
            await message.channel.send("Nothing to Stop")

'''
@Name Skip
@Description Command to Skip current music with one in the queue
@args1 message message that was sent by user
@args2 argument argument of the commands
@return Null
'''
async def skip(message,argument):
    global vc, queue
    if not isinstance(message.channel, discord.channel.DMChannel):
        if message.guild.id not in lock:
            lock[message.guild.id] = False

        if message.guild.id not in vc:
            vc[message.guild.id] = None

        if lock[message.guild.id] and message.author.id not in root:
            await message.channel.send("Sorry i can't")
            return

        try:
            if vc[message.guild.id] == None:
                await message.channel.send("Nothing to skip")
                return

            if nextMusic(vc[message.guild.id], message.guild.id):
                await message.channel.send("Playing")
            else:
                await message.channel.send("Not in queue")

        except Exception as e:
            await message.channel.send("Erreur technique vérifier que se soit une video téléchargeable ou que vous soyez dans un salon vocaux")
            print(e)


'''
@Name active Lock
@Description Active lock to made stop user that use the vocal command in the server only authorize root to use it
@args1 message Message that was sent by user
@args2 argument argument of the commands
@return Null
'''
async def actLock(message,argument):
    global lock

    if not isinstance(message.channel, discord.channel.DMChannel):
        if message.guild.id not in lock:
            lock[message.guild.id] = False

        if lock[message.guild.id]:
            lock[message.guild.id] = False
            await message.channel.send("Lock désactiver")
        else:
            lock[message.guild.id] = True
            await message.channel.send("Lock activer")

# Music commands end

root = []
rootoptions = {}
options = {}

@tasks.loop(seconds = 1)
async def LoopMusic():
    global vc, queue
    for i in vc:
        if vc[i] != None:
            if not vc[i].is_playing():
                if queue[i]:
                    nextMusic(vc[i], i)
                else:
                    await vc[i].disconnect()

                    vc[i] = None
                    queue[i] = []

@client.event
async def on_message(message):
    print("(in "+str(message.channel)+" at "+str(datetime.datetime.now())+")"+str(message.author)+": "+message.content)
    if message.author == client.user:
        return

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

# End Message and Command

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user)
    print(client.user.id)
    print('------')
    LoopMusic.start()

client.run(TOKEN)
