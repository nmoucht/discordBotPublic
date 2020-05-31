import os
from dotenv import load_dotenv

def deleteDownloadedYoutubeFiles():
    for filename in os.listdir("."):
        if(filename.endswith(".mp4") or filename.endswith(".websm") or filename.endswith(".m4a") or filename.startswith("youtube")):
            os.remove(filename)

def getTagsForYoutubeVideos():
    load_dotenv()
    tagTxt = os.getenv('TAGS_FILE')
    dictOfTags = {}
    f = open(tagTxt, "r")
    lines = f.readlines()
    lines.pop(0)
    for line in lines:
        line = line.replace(" ","")
        video = line[line.find("=")+1:line.find("-*-")]
        lineTags = line[line.rfind("-*-")+3:].strip('\n')
        tags = lineTags.split(",")
        dictOfTags[video] = tags
    return dictOfTags

def writeTagsToFile(tagList):
    load_dotenv()
    tagTxt = os.getenv('TAGS_FILE')
    f = open(tagTxt, "w")
    for tagLine in tagList:
        f.write(tagLine+'\n')

def filePathForYoutubeLink(url):
    load_dotenv()
    youtubeFiles = os.getenv("LOCAL_VIDS")
    vids = os.listdir(youtubeFiles)
    for vid in vids:
        print("youtube title:"+getTitleForLink(url))
        print("local:"+vid[:vid.find("-")].lower())
        if(vid[:vid.find("-")].lower() == getTitleForLink(url)):
            return youtubeFiles+"/"+vid
    return ""

def getTitleForLink(url):
    load_dotenv()
    tagTxt = os.getenv('TAGS_FILE')
    dictOfTags = {}
    f = open(tagTxt, "r")
    lines = f.readlines()
    lines.pop(0)
    for line in lines:
        if(line.find(url)!=-1):
            print(url)
            print("sfdgdf")
            return line[line.find("-*-")+3:line.rfind("-*-")]
    return ""

def main():
    print(getTagsForYoutubeVideos())

if __name__ == "__main__": 
    main()