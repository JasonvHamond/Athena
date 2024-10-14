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

# Create general voice files:
# PS: Bad spelling is for good pronounciation.
engine.save_to_file("Hello, I am Athena, what is your name?", "Athena/data/name.wav")
engine.save_to_file("What kind of joke do you want me to tell you?", "Athena/data/joke.wav")
engine.save_to_file("I can't think of any jokes related to that topic", "Athena/data/nojoke.wav")
engine.save_to_file("That's right!", "Athena/data/right.wav")
engine.save_to_file("Have a nice day!", "Athena/data/exit.wav")
engine.save_to_file("What calculation would you like me to perform?", "Athena/data/whatcalc.wav")
engine.save_to_file("Can I help with anything else?", "Athena/data/help.wav")
engine.runAndWait()
engine.stop()

def combine_audio(vidname, audname, outname, fps=60): 
    import moviepy.editor as mpe
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname,fps=fps)

def listen_voice():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source, timeout=20, phrase_time_limit=20)
            return  r.recognize_google(audio)
    except:
        return
        # r.adjust_for_ambient_noise(source, duration=0.2)
        # # Listen to the user
        # user_input = r.listen(source, timeout=20, phrase_time_limit=20)
        # raw_data = user_input.get_raw_data(convert_rate=16000, convert_width=2)
        # # return raw_data
        # return nr.reduce_noise(audio_clip=user_input, noise_clip=raw_data)

# Find matches
def find_match(query, questions):
    # Save the matches
    match: list = get_close_matches(query, questions, n=1, cutoff=0.5)
    # Return matches.
    return match[0] if match else None

# Get the answer.
def get_answer(query, knowledge):
    # Loop through questions
    for question in knowledge["questions"]:
        # Check if question is related to the query
        if(question["question"] == query):
            # Return the answer.
            return question["answer"]
        
# Ask for the user's name
def ask_name():
    # Print out question
    playsound(os.getcwd() + '/Athena/data/name.wav', True)
    # Ask for user's name
    name = listen_voice()
    # Save name.
    knowledge["user"].append({"name": name})
    ath.save_knowledge(os.getcwd() + "/Athena/data/knowledge.json", knowledge)

def search(query):
    # Warn the user
    engine.say("This will open your default browser, do you want to continue?")
    engine.runAndWait()
    engine.stop()
    # Get user's input
    answer = listen_voice()
    # Check for user's consent
    if("yes" in answer.lower() or "continue" in answer.lower()):
        engine.say(f"I am opening your default browser to search for {query}.")
        engine.runAndWait()
        engine.stop()
        # Ready query.
        query = query.replace(" ", "+")
        # Open the default browser
        webbrowser.open_new(f"https://www.google.com/search?q={query}")
    else:
        # Tell user that google won't be opened.
        engine.say("Not opening your default browser.")
        engine.runAndWait()
        engine.stop()
def open_web(query):
    engine.say(f"I am opening {query}.")
    engine.runAndWait()
    engine.stop()
    # Ready query.
    query = query.replace(" ", "").replace("dot", ".")
    if(".com" in query):
        # Open the default browser
        webbrowser.open_new(f"https://www.{query}")
    else:
        # Open the default browser
        webbrowser.open_new(f"https://www.{query}.com")

# Tell a joke
def tell_joke():
    # Speak the mp3 file
    playsound(os.getcwd() + '/Athena/data/joke.wav', True)
    while True:
        try:
            # Get input from user.
            topic = listen_voice()
            break
        except:
            continue
    # Check if topic exists.
    if(any(key in topic for key in knowledge["fun"][0]["jokes"].keys())):
        # Select the topic
        topic = next(key for key in knowledge["fun"][0]["jokes"].keys() if key in topic)
        amount = len(knowledge["fun"][0]["jokes"][topic.lower()])
        joke = knowledge["fun"][0]["jokes"][topic.lower()][random.randint(0, amount-1)]
        # save the joke's question.
        engine.say(joke["question"])
        engine.runAndWait()
        engine.stop()
        # Get user's answer.
        answer = listen_voice()
        # Check if answer is right.
        if(answer.lower() == joke["answer"].lower()):
            # Speak the mp3 file
            playsound(os.getcwd() + '/Athena/data/right.wav', True)
        else:
            engine.say(joke["answer"])
            engine.runAndWait()
            engine.stop()
    else:
        # Speak the mp3 file
        playsound(os.getcwd() + '/Athena/data/nojoke.wav', True)

# Tell a joke
def randomizer(query):
    # Check if topic exists.
    if(any(key in query for key in knowledge["fun"][1]["random"].keys())):
        # Select the topic
        query = next(key for key in knowledge["fun"][1]["random"].keys() if key in query)
        amount = len(knowledge["fun"][1]["random"][query.lower()])
        item = knowledge["fun"][1]["random"][query.lower()][random.randint(0, amount-1)]
        # Say the random game or recipe.
        engine.say(item["name"])
        engine.runAndWait()
        engine.stop()

def math():
    # # Speak the wav file
    # playsound(os.getcwd() + '/Athena/data/whatcalc.wav', True)
    engine.say("What calculation would you like me to perform?")
    engine.runAndWait()
    engine.stop()

    while True:
        try:
            # Get input from user.
            calc = listen_voice()
            break
        except:
            continue
    try:
        calculation = calc.replace("x", "*").replace("^", "**")
        if("√" in calculation):
            calculation = f"np.sqrt({calculation.replace('√', '')})"
        calculated = eval(calculation)
        engine.say(f"{calc} is {calculated}")
        engine.runAndWait()
        engine.stop()
        print(f"{calc} = {calculated}")
    except:
        engine.say(f"A problem occured with the calculation.")
        engine.runAndWait()
        engine.stop()

def play_song(query):
    # Tell the user that loading can take a bit.
    engine.say(f"Playing {query}, this can take a bit to load.")
    engine.runAndWait()
    engine.stop()
    # Create request.
    request = youtube.search().list(
        part = "id,snippet",
        q = query,
        maxResults = 1,
        type = "video"
    )
    # Create response
    response = request.execute()
    # Get results as vid 
    for vid in response["items"]:
        # Get url.
        url = f"https://www.youtube.com/watch?v={vid['id']['videoId']}"
    
    # Get the video
    with YoutubeDL({'extract_audio': True, 'format': 'bestaudio', 'audio_format': 'mp3', 'outtmpl': 'Athena/data/youtube.mp3'}) as video:
        info_dict = video.extract_info(url, download = True)
        video_title = info_dict['title']
        print(video_title)
        # video.download(url)
        print("Download completed")
    audio_clip = AudioFileClip(os.getcwd() + "\Athena\data\youtube.mp3")
    audio_clip.write_audiofile("Athena\data\youtube1.mp3", bitrate="192k")
    # Set the mixer
    mixer.init()
    # Play song
    mixer.music.load(os.getcwd() + "\Athena\data\youtube1.mp3")
    mixer.music.play()
    while True:
        try:
            # Get input from user.
            user_input = listen_voice()
            if("stop" in user_input.lower()):
                mixer.music.stop()
                break
        except:
            continue
    mixer.music.unload()
    os.remove("Athena/data/youtube.mp3")
    os.remove("Athena/data/youtube1.mp3")

def download_yt():
    # Tell the user the instructions.
    engine.say(f"A text file will be opened, enter the URL in this file.")
    engine.runAndWait()
    engine.stop()
    # Open text file in Notepad
    fileName = "Athena\data\youtube_url.txt"
    os.startfile(fileName)
    # Wait until file is updated.
    file_update = False
    while file_update == False:
        with open(fileName, 'r') as file_obj:
            # read first character
            first_char = file_obj.read(1)
        
            if not first_char:
                continue
            else:
                file_update = True
        time.sleep(1)
    # Read the first line of the txt file
    with open(fileName) as f:
        url = f.readline().strip("\n")
    open(fileName, "w").close()
    with YoutubeDL({'extract_audio': False, 'format': 'bestvideo', 'outtmpl': 'Athena/data/youtube.mp4'}) as video:
        info_dict = video.extract_info(url, download = True)
        video_title = info_dict['title']
        print(video_title)
    with YoutubeDL({'extract_audio': True, 'format': 'bestaudio', 'outtmpl': 'Athena/data/youtube.mp3'}) as video:
        info_dict = video.extract_info(url, download = True)
        video_title = info_dict['title']
        print(video_title)
    engine.say(f"What name would you like to give to this file?.")
    engine.runAndWait()
    engine.stop()
    vidname = listen_voice()

    combine_audio("Athena/data/youtube.mp4", "Athena/data/youtube.mp3", f"Athena/data/funny/{vidname}.mp4")
    engine.say(f"Download completed, check Athena/data/{vidname}.mp4 for your downloaded file.")
    engine.runAndWait()
    engine.stop()
    os.remove("Athena/data/youtube.mp3")
    os.remove("Athena/data/youtube.mp4")

def something_funny():
    # Get all files
    files = os.listdir("Athena\\data\\funny")
    os.startfile(f"Athena\\data\\funny\\{random.choice(files)}")

def video_name(query):
    matching = []
    # Get all files 
    directory = "Athena\\data\\funny"
    # Check if there are any files with name
    for file in os.listdir(directory):
        if query.replace(" ", "") in file:
            matching.append(file)
    os.startfile(f"Athena\\data\\funny\\{random.choice(matching)}")

def stopfighting():
    os.startfile(f"Athena\\data\\funny\\dog.jpg")
    # Set the mixer
    mixer.init()
    time.sleep(1)
    # Play song
    mixer.music.load(os.getcwd() + f"/Athena/data/funny/stopfighting.mp3")
    mixer.music.play()

def increase_volume(volume):
    sessions = AudioUtilities.GetAllSessions()
    volume = volume.replace("increaseto", "").replace("decreaseto", "").replace("changeto", "").replace("setto", "")
    volume = float(volume.replace("percent", "").replace("%", ""))
    if(volume > 1.0):
        new_vol = (volume/100)
    else:
        new_vol = volume
    for session in sessions:
        vol = session._ctl.QueryInterface(ISimpleAudioVolume)
        vol.SetMasterVolume(new_vol, None)
    engine.say(f"Volume changed to {volume}")
    engine.runAndWait()
    engine.stop() 
    
def chatbot():
    # Infinite loop
    while True:
        recognize = False
        while recognize == False:
            try:
                # Get input from user.
                user_input = listen_voice()
                if("athena" in user_input.lower()):
                    user_input = user_input.lower().replace("athena ", "")
                    recognize = True
                elif("stop" in user_input.lower()):
                    stopfighting()
                    raise Exception("Stop fighting!")
                else:
                    # Check if there is a video with name.
                    video_name(user_input)
            except:
                recognize = False

        match = find_match(user_input, [question["question"] for question in knowledge["questions"]])
        if("quit" in user_input.lower() or "exit" in user_input.lower()):
            # Speak the mp3 file
            playsound(os.getcwd() + '/Athena/data/exit.wav', True)
            break
        elif("play" in user_input.lower()):
            # Remove play from the query
            query = user_input.replace("play", "")
            # Play the song.
            play_song(query)
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("download" in user_input.lower()):
            # Download the YT video.
            download_yt()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("show" in user_input.lower() and "funny" in user_input.lower()):
            something_funny()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("stop fighting" in user_input.lower()):
            stopfighting()
        elif("current time" in user_input.lower()):
            # Get the current date.
            engine.say(f"Currently, it is {datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')}")
            engine.runAndWait()
            engine.stop()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        # Search for information
        elif("information on" in user_input.lower() or "what is" in user_input.lower() or "who is" in user_input.lower() or "tell me about" in user_input.lower()):
            # Create the right query
            query = user_input.replace("information on", "").replace("tell me about", ""). replace("who is", "").replace("what is", "")
            try:
                # get the result
                result = wikipedia.summary(query, sentences=2)
                # Tell the user about the information
                engine.say("Wikipedia says")
                engine.say(result)
                engine.say(f"Would you like to hear more about {query}?")
                engine.runAndWait()
                engine.stop()
                recognize = False
                while True:
                    try:
                        # Get input from user.
                        user_input = listen_voice()
                        break
                    except:
                        continue
                if("yes" in user_input.lower()):
                    # get the result
                    result = wikipedia.summary(query).replace(".", ". ")
                    # Tell the user about the information
                    engine.save_to_file(result, "Athena/data/result.wav")
                    engine.runAndWait()
                    engine.stop()
                    # Play the audio.
                    mixer.music.load(os.getcwd() + r"\Athena\data\result.wav")
                    mixer.music.play()
                    # Infinite loop.
                    while True:
                        try:
                            # Get input from user.
                            user_input = listen_voice()
                            # If user says stop.
                            if("stop" in user_input.lower()):
                                # Stop audio.
                                mixer.music.stop()
                                break
                        except:
                            continue
                    # Exit audio.
                    mixer.music.unload()
                    os.remove("Athena/data/result.wav")
            except:
                engine.say("I couldn't find information on that topic.")
            engine.runAndWait()
            engine.stop()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("random" in user_input.lower()):
            query = user_input.lower().replace("random", "")
            randomizer(query)
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        # If the user says open.
        elif("open" in user_input.lower()):
            # Create query.
            query = user_input.lower().replace("open", "")
            open_web(query)
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        # If the user says search.
        elif("search" in user_input.lower()):
            # Remove keywords.
            query = user_input.replace("search for", "").replace("search up", "").replace("search", "")
            # Search for query.
            search(query)
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("tell me a joke" in user_input.lower()):
            tell_joke()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("calculate" in user_input.lower() or "math question" in user_input.lower() or "calculation" in user_input.lower()):
            math()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif("volume" in user_input.lower()):
            # Remove volume and spaces from query for easier usage.
            volume = user_input.lower().replace("volume", "").replace(" ", "")
            # Change volume.
            try:
                increase_volume(volume)
            except:
                engine.say("Something went wrong.")
                engine.runAndWait()
                engine.stop()
            playsound(os.getcwd() + "/Athena/data/help.wav", True)
        elif(match):
            # Search for best best answer to question.d
            answer = get_answer(match, knowledge)
            engine.say(answer)
            engine.runAndWait()
            engine.stop()
        else:
            # This happens in console for learning purposes.
            print("What would you like me to answer with?")
            answer = input(">")

            if(answer.lower() != "skip"):
                knowledge["questions"].append({"question": user_input, "answer": answer})
                ath.save_knowledge("Athena/data/knowledge.json", knowledge)
                print("I will keep this in mind.")
            
# Check if user's name is known already.
if len(knowledge["user"]) == 0:
    ask_name()
# Get the user's name
name = knowledge["user"][0]["name"]
engine.say(f"Hello {name}, what can I help you with?")
engine.runAndWait()
engine.stop()
# Run function.
chatbot()
