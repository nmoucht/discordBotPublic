# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
from musicCore import YTDLSource
from interfaceYoutube import YoutubeInterface
from musicCore import MusicCore
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TEST_GUILD = os.getenv('DISCORD_GUILD')#os.getenv('DISCORD_GUILD_TEST')#
YOUTUBE_WATCH = os.getenv('YOUTUBE_WATCH_LINK')
YOUTUBE_PLAYLIST = os.getenv('YOUTUBE_BSMNT_PLAYLIST')
YOUTUBE_API_LINK = os.getenv('YOUTUBE_API_LINK')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
fun = os.getenv('FUN')
funback = os.getenv('FUN_BACK')
helpLink = os.getenv('HELP_LINK')
client = discord.Client()
yt = YoutubeInterface(YOUTUBE_API_KEY, YOUTUBE_API_LINK, YOUTUBE_WATCH, YOUTUBE_PLAYLIST)
bot = commands.Bot(command_prefix = ",")

class Bot(object):
    
    mc = MusicCore("","")
    ok = 0
    def __init__(self):
        self.ok = 0

mybot = Bot()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == TEST_GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    print(message.content)
    if(message.content == fun):
        await message.channel.send(funback)
    if("bs!" in message.content):
        if("keyword" in message.content):
            vids = yt.getVideoListForKeywords(message.content[message.content.find("keyword ")+8:].split(" "))
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            for url in vids:
                mybot.mc.addToQueue(url, bot)
            
            await message.channel.send("Added "+str(len(vids))+" to the queue")
        if("stop" in message.content):
            await mybot.mc.stop()
            await message.channel.send("Leaving")
        if("skip" in message.content):
            mybot.mc.skip(bot)
        if("play" in message.content):
            if(message.content[message.content.find("play")+4:].strip()==""):
                vids = yt.getWholePlaylist()
                if(not mybot.mc.isInitialized()):
                    mybot.mc = MusicCore(message.author.voice.channel, message.channel)
                for url in vids:
                    mybot.mc.addToQueue(url, bot)
                await message.channel.send("Added "+str(len(vids))+" to the queue")
        if("shuffle" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            mybot.mc.shuffle()
            await message.channel.send("Shuffled songs")
        if("help" in message.content):
            await message.channel.send(helpLink)    

client.run(TOKEN)