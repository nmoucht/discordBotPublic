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
TEST_GUILD = os.getenv('DISCORD_GUILD_TEST')
fun = os.getenv('FUN')
funback = os.getenv('FUN_BACK')
helpLink = os.getenv('HELP_LINK')
defaultPlaylist = os.getenv('YOUTUBE_BSMNT_PLAYLIST')
YOUTUBE_WATCH = os.getenv('YOUTUBE_WATCH_LINK')
YOUTUBE_API_LINK = os.getenv('YOUTUBE_API_LINK')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
client = discord.Client()
yt = YoutubeInterface(YOUTUBE_API_KEY, YOUTUBE_API_LINK, YOUTUBE_WATCH)
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
        if("playnext" in message.content):
            if(message.content[message.content.find("playnext")+8:].strip()!=""):
                if("https://www.youtube.com/watch?v=" in message.content):
                    if(not mybot.mc.isInitialized()):
                        mybot.mc = MusicCore(message.author.voice.channel, message.channel)
                    mybot.mc.addToQueueNext(message.content[message.content.find("https://www.youtube.com/watch?v="):], bot)
                    await message.channel.send("Added video next in the queue")
        elif("play" in message.content):
            if(message.content[message.content.find("play")+4:].strip()==""):
                vids = yt.getPlaylistForLink(YOUTUBE_API_LINK, defaultPlaylist, YOUTUBE_API_KEY)
                if(not mybot.mc.isInitialized()):
                    mybot.mc = MusicCore(message.author.voice.channel, message.channel)
                for url in vids:
                    mybot.mc.addToQueue(url, bot)
                await message.channel.send("Added "+str(len(vids))+" to the queue")
            elif("https://www.youtube.com/watch?v=" in message.content):
                if(not mybot.mc.isInitialized()):
                    mybot.mc = MusicCore(message.author.voice.channel, message.channel)
                mybot.mc.addToQueue(message.content[message.content.find("https://www.youtube.com/watch?v="):], bot)
                await message.channel.send("Added video to the queue")
        elif("search" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            keywords = [x.lower() for x in message.content[message.content.find("keyword ")+8:].split(" ")]
            res = mybot.mc.search(keywords, yt, True)
            await message.channel.send("Removed "+str(res[0])+" from the queue. Size now "+str(res[1]))
        elif("revkeyword" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            keywords = [x.lower() for x in message.content[message.content.find("keyword ")+8:].split(" ")]
            res = mybot.mc.keywords(keywords, yt, True)
            await message.channel.send("Removed "+str(res[0])+" from the queue. Size now "+str(res[1]))
        elif("keyword" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            keywords = [x.lower() for x in message.content[message.content.find("keyword ")+8:].split(" ")]
            res = mybot.mc.keywords(keywords, yt, False)
            await message.channel.send("Removed "+str(res[0])+" from the queue. Size now "+str(res[1]))
        elif("revtag" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            tags = [x.lower() for x in message.content[message.content.find("tag ")+4:].split(" ")]
            res = mybot.mc.tags(tags, yt, True)
            await message.channel.send("Removed "+str(res[0])+" from the queue. Size now "+str(res[1]))
        elif("tag" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            tags = [x.lower() for x in message.content[message.content.find("tag ")+4:].split(" ")]
            res = mybot.mc.tags(tags, yt, False)
            await message.channel.send("Removed "+str(res[0])+" from the queue. Size now "+str(res[1]))
        
        elif("shuffle" in message.content):
            if(not mybot.mc.isInitialized()):
                mybot.mc = MusicCore(message.author.voice.channel, message.channel)
            mybot.mc.shuffle()
            await message.channel.send("Shuffled songs")
        elif("stop" in message.content):
            await mybot.mc.stop()
        elif("skip" in message.content):
            mybot.mc.skip(bot)
        elif("help" in message.content):
            await message.channel.send(helpLink)

client.run(TOKEN)