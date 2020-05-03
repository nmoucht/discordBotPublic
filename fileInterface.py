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
        video = line[line.find("=")+1:line.rfind("-")]
        lineTags = line[line.rfind("-")+1:].strip('\n')
        tags = lineTags.split(",")
        dictOfTags[video] = tags
    return dictOfTags

def writeTagsToFile(tagList):
    load_dotenv()
    tagTxt = os.getenv('TAGS_FILE')
    f = open(tagTxt, "w")
    for tagLine in tagList:
        f.write(tagLine+'\n')


def main():
    print(getTagsForYoutubeVideos())

if __name__ == "__main__": 
    main()