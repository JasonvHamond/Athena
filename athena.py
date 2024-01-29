# Import packages
import json
import pandas as pd
import numpy as np
from difflib import get_close_matches

# Load the knowledge from chatbot
def load_knowledge(path):
    # Open the file
    with open(path, "r") as file:
        # Save data
        data: dict = json.load(file)
    return data

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

        
def chatbot():
    # Infinite loop
    while True:
        # Get input from user.
        user_input = input(">")

        if(user_input.lower() == "quit" or user_input.lower() == "exit"):
            print("Athena: Have a nice day!")
            break 

        match = find_match(user_input, [question["question"] for question in knowledge["questions"]])

        if(match):
            answer = "Athena: " + get_answer(match, knowledge)
            print(answer)
        else:
            print("Athena: What would you like me to answer with?")
            answer = input(">")

            if(answer.lower() != "skip"):
                knowledge["questions"].append({"question": user_input, "answer": answer})
                save_knowledge("data/knowledge.json", knowledge)
                print("Athena: I will keep this in mind.")

# Load knowledge data.
knowledge: dict = load_knowledge("data/knowledge.json")

# Check if user's name is known already.
if len(knowledge["user"]) == 0:
    ask_name()
# Get the user's name
name = knowledge["user"][0]["name"]

print(f"Athena: Hello {name}, how are you doing?")

# Run function.
chatbot()