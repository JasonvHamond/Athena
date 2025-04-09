# Import all packages
import pandas as pd
import os
from classes.emotion_classifier import EmotionDetection
from classes.translator import Translator
from classes.transcription import Transcription
import re
from tqdm import tqdm
import warnings
import json

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