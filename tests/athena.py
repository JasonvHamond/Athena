# Import packages
import time 
from chatterbot import ChatBot, trainers
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

# Set time.clock for the chatterbot package.
time.clock = time.time

# Create and initialize chatbot Athena.
chatbot = ChatBot("Athena")
# Train Chatbot.
trainer = ChatterBotCorpusTrainer(chatbot) 
# trainer.train([
#     "Hi",
#     "Hello, how are you doing?",
# ])
# trainer.train([
#     "How are you doing?",
#     "I am doing good",
# ])
# Initialize ways to exit.
exit_conditions = (":q", "quit", "exit")

# Train Chatbot.
# corpus_trainer = ChatterBotCorpusTrainer(chatbot) 
trainer.train('chatterbot.corpus.english')
# trainer.export_for_training("data/knowledge.yml")

# Infinite loop
while True:
    query = input(">")
    # Check if user typed something from the exit_conditions.
    if query in exit_conditions:
        print("Athena: Have a nice day!")
        break
    # Otherwise print out the response.
    else:
        print(f"Athena> {chatbot.get_response(query)}")