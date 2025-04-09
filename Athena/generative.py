from gpt4all import GPT4All
import Athena.athena as ath
import pandas as pd
import numpy as np
from difflib import get_close_matches
import random
import os
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

model = GPT4All(f"{ath.init}\models\llama-2-7b-chat.Q4_0.gguf")

def chatbot():
    ath.engine.say("This is the generative model, what can I help you with?")
    ath.engine.runAndWait()
    ath.engine.stop()
    # Infinite loop
    while True:
        recognize = False
        while recognize == False:
            try:
                # Get input from user.
                user_input = ath.listen_voice()
                if("athena" in user_input.lower()):
                    user_input = user_input.lower().replace("athena ", "")
                    print(user_input)
                    recognize = True
                    response = model.generate(f"{user_input}.")
                    if response is None or response == "":
                        response = model.generate(f"{user_input}.")
                    print(response)
                    ath.engine.say(response)
                    ath.engine.runAndWait()
                    ath.engine.stop()
                elif("stop" in user_input.lower()):
                    ath.stopfighting()
                    raise Exception("Stop fighting!")
                elif("exit" in user_input):
                    recognize = True
                    break
            except:
                recognize = False

            if("quit" in user_input.lower() or "exit" in user_input.lower()):
                    # Speak the mp3 file
                    playsound(f"{ath.init}/data/exit.wav", True)
                    break
