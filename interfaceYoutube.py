from pyyoutube import Api
import urllib.request
import urllib.error
import requests
import json
from dotenv import load_dotenv
import os
from fileInterface import getTagsForYoutubeVideos

class YoutubeVid(object):
    title = ""
    description = ""
    idVid = ""
    tags = []

    # The class "constructor" - It's actually an initializer 
    def __init__(self, title, description, idVid, tags):
        self.title = title
        self.description = description
        self.idVid = idVid
        self.tags = tags

class YoutubePlaylist(object):
    vids = {}
    def __init__(self, vids, tags, watchLink):
        self.vids = {}
        for vid in vids:
            self.vids[watchLink+vid['snippet']['resourceId']['videoId']] = (YoutubeVid(vid['snippet']['title'], vid['snippet']['description'], vid['snippet']['resourceId']['videoId'], tags[vid['snippet']['resourceId']['videoId']]))

    # def getMatchesForKeywords(self, link, keywords):
    #     vidList = []
    #     for video in self.vids:
    #         for keyword in keywords:
    #             if keyword.lower() in self.vids[video].title.lower() or keyword.lower() in self.vids[video].description.lower():
    #                 vidList.append(link+self.vids[video].idVid)
    #     return vidList

    # def getMatchesForTags(self, link, tags):
    #     vidList = []
    #     for video in self.vids:
    #         for tag in tags:
    #             if tag.lower() in [tag.lower() for tag in self.vids[video].tags]:
    #                 vidList.append(link+self.vids[video].idVid)
    #     return vidList
    
    def size(self):
        return len(self.vids)

    def getWholePlaylist(self):
        return list(self.vids.keys())
    
    def getVids(self):
        return self.vids
    
    def getTitleAndDescriptionForLink(self,url):
        return self.vids[url].title + " " + self.vids[url].description

    def getTagsForLink(self, url):
        return [x.lower() for x in self.vids[url].tags]

class YoutubeInterface(object):
    key = ""
    apiLink = ""
    watchLink = ""
    currentPlaylist = YoutubePlaylist([],[], "")
    currentPlaylistLink = ""


    # The class "constructor" - It's actually an initializer 
    def __init__(self, key, apiLink, watchLink):
        self.key = key
        self.apiLink = apiLink
        self.watchLink = watchLink

    def getPlaylistForLink(self, api_link, link, key):
        if(link == self.currentPlaylistLink):
            return self.currentPlaylist
        allVids = []
        link = api_link.format(link,key)
        api_url = link
        while True:
            playlist = json.loads(requests.get(api_url).content)
            allVids.extend(playlist['items'])
        
            try: 
                next_page_token = playlist['nextPageToken']
                api_url = link + '&pageToken={}'.format(next_page_token)
            except:
                break
        self.currentPlaylist = YoutubePlaylist(allVids, getTagsForYoutubeVideos(), self.watchLink)
        self.currentPlaylistLink = link
        return self.getWholePlaylist()
    
    def getWholePlaylist(self):
        return self.currentPlaylist.getWholePlaylist()

    def getTitleAndDescriptionForLink(self, url):
        return self.currentPlaylist.getTitleAndDescriptionForLink(url).lower()
    
    def getTagsForLink(self, url):
        return self.currentPlaylist.getTagsForLink(url)

def main():
    load_dotenv()
    YOUTUBE_WATCH = os.getenv('YOUTUBE_WATCH_LINK')
    YOUTUBE_PLAYLIST = os.getenv('YOUTUBE_BSMNT_PLAYLIST')
    YOUTUBE_API_LINK = os.getenv('YOUTUBE_API_LINK')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

    yt = YoutubeInterface(YOUTUBE_API_KEY, YOUTUBE_API_LINK, YOUTUBE_WATCH, YOUTUBE_PLAYLIST)



if __name__ == "__main__":
    main()