# DATASETS WANTING TO USE:
# "ConvAI3", https://convai.io/data/
# "AmbigQA", https://nlp.cs.washington.edu/ambigqa/

# Import packages
import json
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
import pandas as pd
import os
from Emotion_Classification.classes.emotion_classifier import EmotionDetection
from Emotion_Classification.classes.translator import Translator
from Emotion_Classification.classes.transcription import Transcription
import re
from tqdm import tqdm
import warnings
import json

r = sr.Recognizer()
# Load dotenv
load_dotenv()
# Get youtube API Key
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
init = os.path.dirname(os.path.abspath(__file__))

# Create general voice files:
# PS: Bad spelling is for good pronounciation.
engine.save_to_file("Hello, I am Athena, what is your name?", f"{init}/data/name.wav")
engine.save_to_file("What kind of joke do you want me to tell you?", f"{init}/data/joke.wav")
engine.save_to_file("I can't think of any jokes related to that topic", f"{init}/data/nojoke.wav")
engine.save_to_file("That's right!", f"{init}/data/right.wav")
engine.save_to_file("Have a nice day!", f"{init}/data/exit.wav")
engine.save_to_file("What calculation would you like me to perform?", f"{init}/data/whatcalc.wav")
engine.save_to_file("Can I help with anything else?", f"{init}/data/help.wav")
engine.runAndWait()
engine.stop()

# Load the knowledge from chatbot
def load_knowledge(path):
    # Open the file
    with open(path, "r") as file:
        # Save data
        data: dict = json.load(file)
    return data

# Load knowledge data.
knowledge: dict = load_knowledge(f"{init}/data/knowledge.json")

# Save newly obtained knowledge
def save_knowledge(path, data):
    # Open file
    with open(path, "w") as file:
        # Save data.
        json.dump(data, file, indent=2)

# Find matches
def find_match(query, questions):
    # Save the matches
    match: list = get_close_matches(query, questions, n=1, cutoff=0.6)
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
    print("Athena: Hello, I am Athena, what is your name?")
    # Ask for user's name
    name = input("Name: ")
    
    # Save name.
    knowledge["user"].append({"name": name})
    save_knowledge("data/knowledge.json", knowledge)

def emotion_classification():
    # Ignore warnings
    warnings.filterwarnings("ignore")
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Set working directory to file directory.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Load the config file
    with open("config.json", "r") as f:
        config = json.load(f)
    # Catch the configurations used for the general app
    destination = config["app"]["destination"]
    # Catch the configurations used for the whisper model
    whisper_mode = config["whisper"]["mode"]
    whisper_lang = config["whisper"]["lang"]
    # Catch the configuration used for the translator model
    translator_model = config["translator"]["model"]
    translator_tokenizer = config["translator"]["tokenizer"]
    # Catch the configuration used for the classifier model.
    classifier_model = config["classifier"]["model"]
    classifier_tokenizer = config["classifier"]["tokenizer"]
    classifier_encoder = config["classifier"]["encoder"]

    tqdm.pandas()
    # Initiate all required classes, set different model paths if needed.
    transcriptor = Transcription()
    translator = Translator(model=translator_model, tokenizer=translator_tokenizer)
    classifier = EmotionDetection(model=classifier_model, tokenizer=classifier_tokenizer, encoder=classifier_encoder)

    print("Emotion Classification Pipeline.")
    while True:
        url = input("Please insert a valid YouTube URL that you wish to process and classify:")
        youtube_regex = r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$"
        if re.match(youtube_regex, url):
            print("Valid URL.")
            break
        else:
            # Notify user to try again.
            print("Url is not a valid YouTube URL, please try again.")

    # Notify user the current progress.
    print("Starting download of YouTube video...")

    # Download YouTube video to be used in the pipeline
    transcriptor.yt_video_downloader(url=url, destination=destination)
    # Notify user about progress
    print("Download completed!")
    print("Starting transcribing the video")
    # Transcribe the data
    df = transcriptor.transcribe(mode=whisper_mode, lang=whisper_lang)
    if not df.empty:
        print("Transcription Completed!")
    else:
        print("Transcription Failed, try again.")
        exit()

    # Notify user about progress.
    print("Translating sentences...")
    # Translate each sentence in the DataFrame
    df["Translation"] = df["Sentence"].progress_apply(translator.translate_text)
    print("Translation Finished!")

    # Notify user.
    print("Starting Emotion Classification...")
    # Make predictions using the sentences
    df["Emotion"] = classifier.classify_emotions(df["Sentence"].tolist())
    print("Emotion Classification Completed!")
    # Save the new dataframe into CSV file.
    df.to_csv(f"{transcriptor.base}.csv", index=False)
    print(f"Successfully saved output to: {transcriptor.base}.csv")

def combine_audio(vidname, audname, outname, fps=60): 
    import moviepy.editor as mpe
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname,fps=fps)

def listen_voice():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=10, phrase_time_limit=20)
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
    playsound(f"{init}/data/name.wav", True)
    # Ask for user's name
    name = listen_voice()
    # Save name.
    knowledge["user"].append({"name": name})
    save_knowledge(f"{init}/data/knowledge.json", knowledge)

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
    playsound(f"{init}/data/joke.wav", True)
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
            playsound(f"{init}/data/right.wav", True)
        else:
            engine.say(joke["answer"])
            engine.runAndWait()
            engine.stop()
    else:
        # Speak the mp3 file
        playsound(f"{init}/data/nojoke.wav", True)

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
    # playsound('/Athena/data/whatcalc.wav', True)
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
    audio_clip = AudioFileClip(f"{init}\data\youtube.mp3")
    audio_clip.write_audiofile(f"{init}\data\youtube1.mp3", bitrate="192k")
    # Set the mixer
    mixer.init()
    # Play song
    mixer.music.load(f"{init}\data\youtube1.mp3")
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
    os.remove(f"{init}/data/youtube.mp3")
    os.remove(f"{init}/data/youtube1.mp3")

def download_yt():
    # Tell the user the instructions.
    engine.say(f"A text file will be opened, enter the URL in this file.")
    engine.runAndWait()
    engine.stop()
    # Open text file in Notepad
    fileName = f"{init}\data\youtube_url.txt"
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
    with YoutubeDL({'extract_audio': False, 'format': 'bestvideo', 'outtmpl': f"{init}/data/youtube.mp4"}) as video:
        info_dict = video.extract_info(url, download = True)
        video_title = info_dict['title']
        print(video_title)
    with YoutubeDL({'extract_audio': True, 'format': 'bestaudio', 'outtmpl': f"{init}/data/youtube.mp3"}) as video:
        info_dict = video.extract_info(url, download = True)
        video_title = info_dict['title']
        print(video_title)
    engine.say(f"What name would you like to give to this file?.")
    engine.runAndWait()
    engine.stop()
    vidname = listen_voice()

    combine_audio(f"{init}/data/youtube.mp4", f"{init}/data/youtube.mp3", f"{init}/data/funny/{vidname}.mp4")
    engine.say(f"Download completed, check Athena/data/{vidname}.mp4 for your downloaded file.")
    engine.runAndWait()
    engine.stop()
    os.remove(f"{init}/data/youtube.mp3")
    os.remove(f"{init}/data/youtube.mp4")

def something_funny():
    # Get all files
    files = os.listdir(f"{init}\\data\\funny")
    os.startfile(f"{init}\\data\\funny\\{random.choice(files)}")

def video_name(query):
    matching = []
    # Get all files 
    directory = f"{init}\\data\\funny"
    # Check if there are any files with name
    for file in os.listdir(directory):
        if query.replace(" ", "") in file:
            matching.append(file)
    os.startfile(f"{init}\\data\\funny\\{random.choice(matching)}")

def stopfighting():
    os.startfile(f"{init}\\data\\funny\\dog.jpg")
    # Set the mixer
    mixer.init()
    time.sleep(1)
    # Play song
    mixer.music.load(f"{init}/data/funny/stopfighting.mp3")
    mixer.music.play()

def objection(query):
    phrases = ["better", "should", "could", "you", " i ", "worse", "is not", "is"]
    anti = ["Worse", "Should not", "Could not", "I", " You ", "Better", "Is", "Is Not"]
    i = 0
    new_q = ""
    for phrase in phrases:
        if phrase in query:
            new_q = query.replace(phrase, anti[i])
        i+=1
    os.startfile(f"{init}\\data\\funny\\objectionscream\\objection.png")
    # Set the mixer
    mixer.init()
    time.sleep(1)
    # Play sfx
    mixer.music.load(f"{init}/data/funny/objectionscream/phoenix-objection.mp3")
    mixer.music.play()
    # Initiate list
    objection = []
    # Add all files to list.
    for file in os.listdir(f"{init}\\data\\funny\\objection"):
        objection.append(file)
    # Play the actual song
    mixer.init()
    time.sleep(1)
    file = random.choice(objection)
    # Play music
    mixer.music.load(f"{init}/data/funny/objection/{file}")
    mixer.music.set_volume(0.2)
    mixer.music.play()
    engine.say(f"Your honor, nuh uh! {new_q}")
    engine.runAndWait()
    engine.stop() 

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
            playsound(f"{init}/data/exit.wav", True)
            break
        elif("play" in user_input.lower()):
            # Remove play from the query
            query = user_input.replace("play", "")
            # Play the song.
            play_song(query)
            playsound(f"{init}/data/help.wav", True)
        elif("download" in user_input.lower()):
            # Download the YT video.
            download_yt()
            playsound(f"{init}/data/help.wav", True)
        elif("show" in user_input.lower() and "funny" in user_input.lower()):
            something_funny()
            playsound(f"{init}/data/help.wav", True)
        elif("stop fighting" in user_input.lower()):
            stopfighting()
        elif("in my opinion" in user_input.lower() or "i think" in user_input.lower()):
            objection(user_input)
        elif("current time" in user_input.lower()):
            # Get the current date.
            engine.say(f"Currently, it is {datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')}")
            engine.runAndWait()
            engine.stop()
            playsound(f"{init}/data/help.wav", True)
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
                    engine.save_to_file(result, f"{init}/data/result.wav")
                    engine.runAndWait()
                    engine.stop()
                    # Play the audio.
                    mixer.music.load(f"\Athena\data\result.wav")
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
                    os.remove(f"{init}/data/result.wav")
            except:
                engine.say("I couldn't find information on that topic.")
            engine.runAndWait()
            engine.stop()
            playsound(f"{init}/data/help.wav", True)
        elif("random" in user_input.lower()):
            query = user_input.lower().replace("random", "")
            randomizer(query)
            playsound(f"{init}/data/help.wav", True)
        # If the user says open.
        elif("open" in user_input.lower()):
            # Create query.
            query = user_input.lower().replace("open", "")
            open_web(query)
            playsound(f"{init}/data/help.wav", True)
        # If the user says search.
        elif("search" in user_input.lower()):
            # Remove keywords.
            query = user_input.replace("search for", "").replace("search up", "").replace("search", "")
            # Search for query.
            search(query)
            playsound(f"{init}/data/help.wav", True)
        elif("tell me a joke" in user_input.lower()):
            tell_joke()
            playsound(f"{init}/data/help.wav", True)
        elif("calculate" in user_input.lower() or "math question" in user_input.lower() or "calculation" in user_input.lower()):
            math()
            playsound(f"{init}/data/help.wav", True)
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
            playsound(f"{init}/data/help.wav", True)
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
                save_knowledge("Athena/data/knowledge.json", knowledge)
                print("I will keep this in mind.")