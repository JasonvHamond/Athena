# Import packages.
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
from yt_dlp import YoutubeDL
from moviepy.editor import AudioFileClip
from difflib import get_close_matches
import random
from playsound import playsound
import speech_recognition as sr
import winsound
import Athena.athena as ath
import Athena.generative as gen
import noisereduce as nr  
import webbrowser
import pyttsx3
import wikipedia
import datetime
from pygame import mixer
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
import time
import ffmpeg

# Load knowledge data.
knowledge = ath.knowledge
r = sr.Recognizer()
# Load dotenv
load_dotenv()
# Get youtube API Key
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# init = os.path.dirname(os.path.abspath(__file__))
         
# Check if user's name is known already.
if len(knowledge["user"]) == 0:
    ath.ask_name()
# Get the user's name
name = knowledge["user"][0]["name"]
engine.say(f"Hello {name}, what can I help you with?")
engine.runAndWait()
engine.stop()

engine.say(f"Do you want to use the generative or original functionalities?")
engine.runAndWait()
engine.stop()
response = ath.listen_voice()
print(response)
if "gen" in response:
    gen.chatbot()
elif "original" in response:
    # Run function.
    ath.chatbot()
else:
    engine.say(f"Closing the program, have a nice day.")
    engine.runAndWait()
    engine.stop()
