# Import packages
import time 
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

# Set time.clock for the chatterbot package.
time.clock = time.time

# Create and initialize chatbot Athena.
chatbot = ChatBot("Athena")
# Train Chatbot.
trainer = ListTrainer(chatbot)
trainer.train([
    "Hi",
    "Hello, how are you doing?",
])
trainer.train([
    "How are you doing?",
    "I am doing good",
])
# Initialize ways to exit.
exit_conditions = (":q", "quit", "exit")

# Train Chatbot.
corpus_trainer=ChatterBotCorpusTrainer(chatbot) 
corpus_trainer.train('chatterbot.corpus.english')

# Infinite loop
while True:
    query = input(">")
    # Check if user typed something from the exit_conditions.
    if query in exit_conditions:
        break
    # Otherwise print out the response.
    else:
        print(f"Athena> {chatbot.get_response(query)}")