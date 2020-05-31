# import vlc
from dotenv import load_dotenv
import os
load_dotenv()
youtubeFiles = os.getenv("LOCAL_VIDS")
vids = os.listdir(youtubeFiles)
from pygame import mixer  # Load the popular external library

mixer.init()
for vid in vids:
    # print(youtubeFiles+"/"+vid)

    mixer.music.load("JoJo Opening 1 Full _ Sono Chi no Sadame-jXYN_M2RDLQ.mp3")
    mixer.music.play()