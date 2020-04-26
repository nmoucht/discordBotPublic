from pyyoutube import Api
import urllib.request
import urllib.error
import requests
import json
from dotenv import load_dotenv
import os

class YoutubeVid(object):
    title = ""
    description = ""
    idVid = ""

    # The class "constructor" - It's actually an initializer 
    def __init__(self, title, description, idVid):
        self.title = title
        self.description = description
        self.idVid = idVid

class YoutubePlaylist(object):
    vids = []
    def __init__(self, vids):
        self.vids = []
        for vid in vids:
            self.vids.append(YoutubeVid(vid['snippet']['title'], vid['snippet']['description'], vid['snippet']['resourceId']['videoId']))

    def getMatchesForKeywords(self, link, keywords):
        vidList = []
        for video in self.vids:
            for keyword in keywords:
                if keyword.lower() in video.title.lower() or keyword.lower() in video.description.lower():
                    vidList.append(link+video.idVid)
        return vidList
    
    def size(self):
        return len(self.vids)

class YoutubeInterface(object):
    key = ""
    apiLink = ""
    watchLink = ""
    playlistID = ""
    youtubeVids = YoutubePlaylist([])


    # The class "constructor" - It's actually an initializer 
    def __init__(self, key, apiLink, watchLink, playlistID):
        self.key = key
        self.apiLink = apiLink
        self.watchLink = watchLink
        self.playlistID = playlistID
        self.youtubeVids = self.getPlaylistForLink(apiLink.format(playlistID,key)) 

    def getPlaylistForLink(self, link):
        allVids = []
        
        api_url= link
        while True:
            playlist = json.loads(requests.get(api_url).content)
            allVids.extend(playlist['items'])
        
            try:
                next_page_token = playlist['nextPageToken']
                api_url = link + '&pageToken={}'.format(next_page_token)
            except:
                break
        return YoutubePlaylist(allVids)
    
    def getWholePlaylist(self):
        return self.youtubeVids.getMatchesForKeywords(self.watchLink, [""])

    def getVideoListForKeywords(self, keywords):
        return self.youtubeVids.getMatchesForKeywords(self.watchLink, keywords)

def main():
    load_dotenv()
    YOUTUBE_WATCH = os.getenv('YOUTUBE_WATCH_LINK')
    YOUTUBE_PLAYLIST = os.getenv('YOUTUBE_BSMNT_PLAYLIST')
    YOUTUBE_API_LINK = os.getenv('YOUTUBE_API_LINK')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

    yt = YoutubeInterface(YOUTUBE_API_KEY, YOUTUBE_API_LINK, YOUTUBE_WATCH, YOUTUBE_PLAYLIST)
    print(yt.getVideoListForKeywords(["jojo"]))

if __name__ == "__main__":
    main()