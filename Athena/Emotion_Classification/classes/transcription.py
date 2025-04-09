# import required packages
from pytubefix import YouTube
import torch
import os
import pandas as pd
import whisper
import re

class Transcription:
    def __init__(self):
        # Initialise variables
        self.url = None
        self.dest = None
        self.filename = None
        self.title = None
        self.base = None
        # Set device to use for whisper
        # Try to use GPU, if not possible then change back to CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

    def yt_video_downloader(self, url, destination):
        """
        Takes a valid URL of a YouTube video, downloads it and saves it into specified location.

        -------------
        Parameters: 
        - url, string: Valid YouTube URL
        - destination, string: folder to save the video in.
        """
        try:
            # Set the URL variable
            self.url = url
            self.dest = destination

            # url input from youtube
            yt = YouTube(self.url)

            # extract only audio
            video = yt.streams.filter(only_audio=True).first()

            # Get the filepath for this video once downloaded.
            self.title = video.title
            file_path = os.path.join(destination, f"{self.title}.mp3")

            # Check if the file already exists
            if os.path.exists(file_path):
                # Delete file if it already exists
                os.remove(file_path)
                print(f"File already exists. Removed the existing file: {file_path}")

            # set destination to save file
            destination = (self.dest)

            # download the file
            out_file = video.download(output_path=destination)

            # save the file
            base, ext = os.path.splitext(out_file)
            # Save the base repo for future use
            self.base = base
            filename = base + '.mp3'
            os.rename(out_file, filename)
            # Save filename for future use
            self.filename = f"{filename}"
        except Exception as ex:
            print(f"An error occured while trying to download a YouTube video: {ex}")
    
    def transcribe(self, mode, lang):
        """
        Takes the file of the last downloaded YouTube Video by yt_video_downloader() and creates a transcription. 
        This transcription is split by start and end time of a sentence.
        -------------
        Returns:
        - pandas.DataFrame: DataFrame containing the following columns: Start Time, End Time, Sentence. 
        """
        try: 
            # Load the specified model
            model = whisper.load_model(mode).to(self.device)
            audio = self.filename
            # Transcribe the mp3 file
            result = model.transcribe(audio, language=lang)
            # Extract segment data
            segments = result["segments"]

            # Process segments to contain timestamps in structured format.
            transcript_data = []
            for seg in segments:
                start_time = self.format_timestamp(seg["start"])
                end_time = self.format_timestamp(seg["end"])
                text = seg["text"].strip()

                transcript_data.append([start_time, end_time, text])
            
            # Delete file to avoid problems with double files
            os.remove(self.filename)

            # Return the dataframe.
            return pd.DataFrame(transcript_data, columns=["Start Time", "End Time", "Sentence"])
        except Exception as ex:
            print(f"Something went wrong while transcribing audio: {ex}")
            return None
            
    @staticmethod
    def format_timestamp(seconds):
        """
        Convert seconds to timestamp format: HH:MM:SS,mmm

        Parameters:
        - seconds, the time in seconds

        Returns:
        - timestamp: HH:MM:SS,mmm
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
