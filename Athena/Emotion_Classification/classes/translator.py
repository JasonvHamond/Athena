# Import required packages
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import pandas as pd

class Translator():
    def __init__(self, model, tokenizer):
        # Load the model and tokenizer.
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)

    # Initiate function to translate the texts in the dataframe
    def translate_text(self, text):
        """
        Takes a Dutch sentence and translates it to English.
        -------------
        Parameters: 
        - text, string: Dutch sentence to be translated

        Returns:
        - translated text, string: English translated sentence.
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        # Tokenize the sentence
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        # Generate the translation
        output_ids = self.model.generate(**inputs)
        # Decode translation
        translated_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        return translated_text