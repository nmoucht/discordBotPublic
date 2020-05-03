import youtube_dl
import discord
import asyncio
import os
import random
from fileInterface import deleteDownloadedYoutubeFiles
from interfaceYoutube import YoutubeInterface
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp4',
        'preferredquality': '192',
    }],
    'cachedir' : False    
}

ffmpeg_options = {
    'options': '-vn -max_error_rate 100 -ignore_unknown'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, executable="/Users/nikosm/Documents/discordBotPublic/ffmpeg"), data=data)

class MusicSong:
    url = ""
    origin = ""

    def __init__(self, url, origin):
        self.url = url
        self.origin = origin
    
    def isEmpty(self):
        return url == ""

class MusicQueue:
    queue = []

    def _init__(self):
        self.queue = []
    
    def top(self):
        if len(self.queue)==0:
            return MusicSong("","")
        return self.queue[0]
    
    def pop(self):
        if(len(self.queue) != 0):
            self.queue.pop(0)
    
    def clear(self):
        if(len(self.queue)!=0):
            self.queue.clear()

    def push(self, item):
        self.queue.append(item)
    
    def pushNext(self, item):
        if(len(self.queue) < 1):
            self.queue.append(item)
            return
        self.queue.insert(1,item)
    
    def isEmpty(self):
        return len(self.queue)==0
    
    def shuffle(self):
        if len(self.queue)!=0:
            top = self.top()
            self.pop()
            random.shuffle(self.queue)
            self.queue.insert(0, top)
    
    def size(self):
        return len(self.queue)
    
    def filterByTags(self, tags, playlistInfo, isRev):
        if(len(self.queue)==0):
            return 0
        originalSize = len(self.queue)
        newQueue = [self.queue[0]]
        for i in range(1,len(self.queue)):
            inTag = False 
            tagsSet = set(tags)
            vidtagsSet = set([tagnew.lower() for tagnew in playlistInfo.getTagsForLink(self.queue[i].url)])
            if(len(tagsSet.intersection(vidtagsSet))==0):
                if(isRev):
                    newQueue.append(self.queue[i])
            else:
                if(not isRev):
                    newQueue.append(self.queue[i])
                
        self.queue = newQueue
        return originalSize - len(self.queue)

    def filterByKeywords(self, keywords, playlistInfo, isRev):
        if(len(self.queue)==0):
            return 0
        originalSize = len(self.queue)
        newQueue = [self.queue[0]]
        for i in range(1,len(self.queue)):
            inKeyword = False
            for keyword in keywords:
                if keyword.lower() in playlistInfo.getTitleAndDescriptionForLink(self.queue[i].url).lower():
                    inKeyword = True
                    break
            if(inKeyword):
                if(not isRev):
                    newQueue.append(self.queue[i])
            else:
                if(isRev):
                    newQueue.append(self.queue[i])
        self.queue = newQueue
        return originalSize - len(self.queue)
    
    def searchByKeywords(self, keywords, playlistInfo, isRev):
        if(len(self.queue)==0):
            return 0
        originalSize = len(self.queue)
        newQueue = [self.queue[0]]
        for i in range(1,len(self.queue)):
            inKeyword = True
            for keyword in keywords:
                if keyword.lower() not in playlistInfo.getTitleAndDescriptionForLink(self.queue[i].url).lower():
                    inKeyword = False
                    break
            if(inKeyword):
                if(not isRev):
                    newQueue.append(self.queue[i])
            else:
                if(isRev):
                    newQueue.append(self.queue[i])
        self.queue = newQueue
        return originalSize - len(self.queue)

class MusicPlayer:
    player = ""
    empty = True
    bot = ""
    url = ""

    def __init__(self, url, bot):
        if url != "":
            self.player = ""
            self.empty = False
            self.bot = bot
            self.url = url
    
    def isEmpty(self):
        return self.empty
    
    async def getPlayer(self):
        return await YTDLSource.from_url(self.url, loop=self.bot.loop, stream=False)
        

class MusicCore(object):
    channel = ""
    textChannel = ""
    player = MusicPlayer("","")
    queue = MusicQueue()
    voice = ""
    isInit = False
    isPlaying = False

    def __init__(self, channel, textChannel):
        self.channel = channel
        self.textChannel = textChannel
        if(not channel == ""):
            self.isInit = True

    def addToQueue(self, url, bot):
        self.queue.push(MusicSong(url, "youtube"))
        if(not self.isPlaying):
            self.isPlaying = True
            asyncio.ensure_future(self.play(bot))
    
    def addToQueueNext(self, url, bot):
        self.queue.pushNext(MusicSong(url, "youtube"))
        if(not self.isPlaying):
            self.isPlaying = True
            asyncio.ensure_future(self.play(bot))

    async def play(self, bot):
        try: 
            self.voice = await self.channel.connect()
        except:
            print("Already connected")
        while(not self.queue.isEmpty()):
            self.player = MusicPlayer(self.queue.top().url, bot)
            await self.textChannel.send(self.queue.top().url)
            p = await self.player.getPlayer()
            try:
                self.voice.play(p, after=lambda e: print('Player error: %s' % e) if e else None)
            except:
                print("Already playing")
            
            while self.voice.is_playing() or self.voice.is_paused():
                await asyncio.sleep(1)
            self.queue.pop()
            self.player = MusicPlayer("", "")
            deleteDownloadedYoutubeFiles()
        self.voice.stop()
        self.isPlaying = False
        await self.voice.disconnect()
        await self.textChannel.send("Leaving, queue is empty")
    
    async def stop(self):
        if(self.player.isEmpty()):
            print("Nothing is plying")
        else:
            self.voice.stop()
            await self.voice.disconnect()
        self.queue.clear()

    def skip(self, bot):
        if(self.player.isEmpty()):
            print("Nothing is playing")
        else:
            self.voice.stop()
    
    def pause(self):
        if(self.player.isEmpty()):
            print("Nothing is playing")
        else:
            self.voice.pause()

    def resume(self):
        if(self.player.isEmpty()):
            print("Nothing is playing")
        else:
            self.voice.resume()

    def shuffle(self):
        self.queue.shuffle()
    
    def tags(self, tags, playlistInfo, isRev):
        return [self.queue.filterByTags(tags, playlistInfo, isRev), self.queue.size()]

    def keywords(self, keywords, playlistInfo, isRev):
        return [self.queue.filterByKeywords(keywords, playlistInfo, isRev), self.queue.size()]
    
    def search(self, keywords, playlistInfo, isRev):
        return [self.queue.searchByKeywords(keywords, playlistInfo, isRev), self.queue.size()]

    def isInitialized(self):
        return self.isInit