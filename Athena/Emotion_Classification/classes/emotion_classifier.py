# Import required packages
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from classes.emotion_dataset import EmotionDataset
import torch
from torch.utils.data import DataLoader
from torch.nn.functional import softmax
import joblib

class EmotionDetection():
    def __init__(self, model, tokenizer, encoder):
        # Load the model and tokenizer.
        self.model = AutoModelForSequenceClassification.from_pretrained(model)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.label_encoder = joblib.load(encoder)
        self.class_names = list(self.label_encoder.classes_)  

    def classify_emotions(self, X):
        """
        Takes a list of Dutch sentences and predicts the emotion for each sentence.
        -------------
        Parameters: 
        - X, list: list of Dutch sentences for which emotions should be predicted.

        Returns:
        - list of predicted emotions.
        """
        try:
            # Convert dataset to be usable in the model.
            test_encodings_ep = self.tokenizer(X, truncation=True, padding=True)
            # Create the datasets correctly
            test_dataset_ep = EmotionDataset(test_encodings_ep)
            test_loader_ep = DataLoader(test_dataset_ep, batch_size=8, shuffle=False)

            all_preds = []
            # Set up the model for evaluation.
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(device)
            self.model.eval()
            # Make predictions using the dataloader and torch
            with torch.no_grad():
                for batch in test_loader_ep:
                    # Get the batch as dictionary
                    batch = {key: val.to(device) for key, val in batch.items()}
                    
                    inputs = {
                        "input_ids": batch["input_ids"],
                        "attention_mask": batch["attention_mask"]
                    }

                    outputs = self.model(**inputs)
                    logits = outputs.logits

                    # Convert logits to predictions
                    probs = softmax(logits, dim=1)
                    preds = torch.argmax(probs, dim=1)

                    all_preds.extend(preds.cpu().numpy())
            # Extract labelname from the LabelEncoder
            predicted_labels = [self.class_names[pred] for pred in all_preds]
            # Return the labels of the predictions.
            return predicted_labels
        except Exception as ex:
            print(f"An error occured during classification of emotions: {ex}")