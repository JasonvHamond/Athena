# import packages
import torch

class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        # Initiate the variables
        self.encodings = encodings
    
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        return item

    def __len__(self):
        return len(next(iter(self.encodings.values())))