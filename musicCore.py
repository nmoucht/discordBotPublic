import youtube_dl
import discord
import asyncio
import os
import random

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
    }]
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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, executable="/Users/nikosm/Documents/discordBot/ffmpeg"), data=data)

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
    
    def isEmpty(self):
        return len(self.queue)==0
    
    def shuffle(self):
        if len(self.queue)!=0:
            top = self.top()
            self.pop()
            random.shuffle(self.queue)
            self.queue.insert(0, top)

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

    async def play(self, bot):
        try: 
            self.voice = await self.channel.connect()
        except:
            print("already connected")
        while(not self.queue.isEmpty()):
            self.player = MusicPlayer(self.queue.top().url, bot)
            await self.textChannel.send(self.queue.top().url)
            p = await self.player.getPlayer()
            try:
                self.voice.play(p, after=lambda e: print('Player error: %s' % e) if e else None)
            except:
                print("playing")
            
            while self.voice.is_playing():
                await asyncio.sleep(1)
            self.queue.pop()
            self.player = MusicPlayer("", "")
            for filename in os.listdir("."):
                if(filename.endswith(".mp4") or filename.endswith(".websm") or filename.endswith(".m4a") or filename.startswith("youtube")):
                    os.remove(filename)

        self.voice.stop()
        await self.voice.disconnect()
    
    async def stop(self):
        if(self.player.isEmpty()):
            print("ok")
        else:
            self.voice.stop()
            await self.voice.disconnect()
        self.queue.clear()

    def skip(self, bot):
        if(self.player.isEmpty()):
            print("ok")
        else:
            self.voice.stop()

    def shuffle(self):
        self.queue.shuffle()


    def isInitialized(self):
        return self.isInit
 
# Hyper fast Audio and Video encoder
# usage: ffmpeg [options] [[infile options] -i infile]... {[outfile options] outfile}...

# Getting help:
#     -h      -- print basic options
#     -h long -- print more options
#     -h full -- print all options (including all format and codec specific options, very long)
#     -h type=name -- print all options for the named decoder/encoder/demuxer/muxer/filter/bsf/protocol
#     See man ffmpeg for detailed description of the options.

# Print help / information / capabilities:
# -L                  show license
# -h topic            show help
# -? topic            show help
# -help topic         show help
# --help topic        show help
# -version            show version
# -buildconf          show build configuration
# -formats            show available formats
# -muxers             show available muxers
# -demuxers           show available demuxers
# -devices            show available devices
# -codecs             show available codecs
# -decoders           show available decoders
# -encoders           show available encoders
# -bsfs               show available bit stream filters
# -protocols          show available protocols
# -filters            show available filters
# -pix_fmts           show available pixel formats
# -layouts            show standard channel layouts
# -sample_fmts        show available audio sample formats
# -colors             show available color names
# -sources device     list sources of the input device
# -sinks device       list sinks of the output device
# -hwaccels           show available HW acceleration methods

# Global options (affect whole program instead of just one file):
# -loglevel loglevel  set logging level
# -v loglevel         set logging level
# -report             generate a report
# -max_alloc bytes    set maximum size of a single allocated block
# -y                  overwrite output files
# -n                  never overwrite output files
# -ignore_unknown     Ignore unknown stream types
# -filter_threads     number of non-complex filter threads
# -filter_complex_threads  number of threads for -filter_complex
# -stats              print progress report during encoding
# -max_error_rate maximum error rate  ratio of errors (0.0: no errors, 1.0: 100% errors) above which ffmpeg returns an error instead of success.
# -bits_per_raw_sample number  set the number of bits per raw sample
# -vol volume         change audio volume (256=normal)

# Per-file main options:
# -f fmt              force format
# -c codec            codec name
# -codec codec        codec name
# -pre preset         preset name
# -map_metadata outfile[,metadata]:infile[,metadata]  set metadata information of outfile from infile
# -t duration         record or transcode "duration" seconds of audio/video
# -to time_stop       record or transcode stop time
# -fs limit_size      set the limit file size in bytes
# -ss time_off        set the start time offset
# -sseof time_off     set the start time offset relative to EOF
# -seek_timestamp     enable/disable seeking by timestamp with -ss
# -timestamp time     set the recording timestamp ('now' to set the current time)
# -metadata string=string  add metadata
# -program title=string:st=number...  add program with specified streams
# -target type        specify target file type ("vcd", "svcd", "dvd", "dv" or "dv50" with optional prefixes "pal-", "ntsc-" or "film-")
# -apad               audio pad
# -frames number      set the number of frames to output
# -filter filter_graph  set stream filtergraph
# -filter_script filename  read stream filtergraph description from a file
# -reinit_filter      reinit filtergraph on input parameter changes
# -discard            discard
# -disposition        disposition

# Video options:
# -vframes number     set the number of video frames to output
# -r rate             set frame rate (Hz value, fraction or abbreviation)
# -s size             set frame size (WxH or abbreviation)
# -aspect aspect      set aspect ratio (4:3, 16:9 or 1.3333, 1.7777)
# -bits_per_raw_sample number  set the number of bits per raw sample
# -vn                 disable video
# -vcodec codec       force video codec ('copy' to copy stream)
# -timecode hh:mm:ss[:;.]ff  set initial TimeCode value.
# -pass n             select the pass number (1 to 3)
# -vf filter_graph    set video filters
# -ab bitrate         audio bitrate (please use -b:a)
# -b bitrate          video bitrate (please use -b:v)
# -dn                 disable data

# Audio options:
# -aframes number     set the number of audio frames to output
# -aq quality         set audio quality (codec-specific)
# -ar rate            set audio sampling rate (in Hz)
# -ac channels        set number of audio channels
# -an                 disable audio
# -acodec codec       force audio codec ('copy' to copy stream)
# -vol volume         change audio volume (256=normal)
# -af filter_graph    set audio filters

# Subtitle options:
# -s size             set frame size (WxH or abbreviation)
# -sn                 disable subtitle
# -scodec codec       force subtitle codec ('copy' to copy stream)
# -stag fourcc/tag    force subtitle tag/fourcc
# -fix_sub_duration   fix subtitles duration
# -canvas_size size   set canvas size (WxH or abbreviation)
# -spre preset        set the subtitle options to the indicated preset

