# Import packages.
import os
import pandas as pd
import numpy as np
from difflib import get_close_matches
import random
from text_to_speech import save
from playsound import playsound
import speech_recognition as sr
import winsound
import Athena.athena as ath
import re

# Load knowledge data.
knowledge = ath.knowledge
r = sr.Recognizer()

# Create general voice files:
# PS: Bad spelling is for good pronounciation.
save("Hello, I am Athayna, what is your name?", "en", file="Athena/data/name.mp3")
save("What kind of joke do you want me to tell you?", "en", file="Athena/data/joke.mp3")
save("I can't think of any jokes related to that topic", "en", file="Athena/data/nojoke.mp3")
save("That's right!", "en", file="Athena/data/right.mp3")
save("Have a nice day!", "en", file="Athena/data/exit.mp3")
save("What calculation would you like me to perform?", "en", file="Athena/data/whatcalc.mp3")

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
    playsound(os.getcwd() + '/Athena/data/name.mp3', True)
    # Ask for user's name
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        frequency = 1000
        duration = 100
        winsound.Beep(frequency, duration)
        audio = r.listen(source)

        name = r.recognize_google(audio)
    
    # Save name.
    knowledge["user"].append({"name": name})
    ath.save_knowledge(os.getcwd() + "/Athena/data/knowledge.json", knowledge)

# Tell a joke
def tell_joke():
    # Speak the mp3 file
    playsound(os.getcwd() + '/Athena/data/joke.mp3', True)
    # Get the topic
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        frequency = 1000
        duration = 100 
        winsound.Beep(frequency, duration)
        audio = r.listen(source)

        topic = r.recognize_google(audio)
    # Check if topic exists.
    if(any(key in topic for key in knowledge["fun"][0]["jokes"].keys())):
        # Select the topic
        topic = next(key for key in knowledge["fun"][0]["jokes"].keys() if key in topic)
        amount = len(knowledge["fun"][0]["jokes"][topic.lower()])
        joke = knowledge["fun"][0]["jokes"][topic.lower()][random.randint(0, amount-1)]
        # save the joke's question.
        save(joke["question"], "en", file="Athena/data/jokequestion.mp3")
        # Speak the mp3 file
        playsound(os.getcwd() + '/Athena/data/jokequestion.mp3', True)
        os.remove("Athena/data/jokequestion.mp3")
        # Get user's answer.
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2) 
            winsound.Beep(1000, 100)
            audio = r.listen(source)
            # Save answer
            answer = r.recognize_google(audio)
        # Check if answer is right.
        if(answer.lower() == joke["answer"].lower()):
            # Speak the mp3 file
            playsound(os.getcwd() + '/Athena/data/right.mp3', True)
        else:
            save(joke["answer"], "en", file="Athena/data/jokeanswer.mp3")
            # Speak the mp3 file
            playsound(os.getcwd() + '/Athena/data/jokeanswer.mp3', True)
            os.remove("Athena/data/jokeanswer.mp3")
    else:
        # Speak the mp3 file
        playsound(os.getcwd() + '/Athena/data/nojoke.mp3', True)

def math():
    # Speak the mp3 file
    playsound(os.getcwd() + '/Athena/data/whatcalc.mp3', True)
    # Get user's answer.
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2) 
        winsound.Beep(1000, 100)
        audio = r.listen(source)
        # Save answer
        calc = r.recognize_google(audio)
    calculation = calc.replace("x", "*").replace("^", "**")
    if("√" in calculation):
        calculation = f"np.sqrt({calculation.replace('√', '')})"
    calculated = eval(calculation)
    save(f"{calc} is {calculated}", "en", file="Athena/data/calculation.mp3")
    print(f"{calc} is {calculated}")
    # Speak the mp3 file
    playsound(os.getcwd() + '/Athena/data/calculation.mp3', True)
    os.remove("Athena/data/calculation.mp3")

def chatbot():
    # Infinite loop
    while True:
        # Get input from user.
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2) 
            winsound.Beep(1000, 100)
            audio = r.listen(source)
            # Save answer
            user_input = r.recognize_google(audio)

        match = find_match(user_input, [question["question"] for question in knowledge["questions"]])
        if(user_input.lower() == "quit" or user_input.lower() == "exit"):
            # Speak the mp3 file
            playsound(os.getcwd() + '/Athena/data/exit.mp3', True)
            break
        elif("tell me a joke" in user_input.lower()):
            tell_joke()
        elif("calculate" in user_input.lower() or "math question" in user_input.lower() or "calculation" in user_input.lower()):
            math()
        elif(match):
            answer = get_answer(match, knowledge)
            save(answer, "en", file="data/answer.mp3")
            # Speak the mp3 file
            playsound(os.getcwd() + '/Athena/data/answer.mp3', True)
            
            os.remove("Athena/data/answer.mp3")
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

# save the joke's question.
save(f"Hello {name}, what can I help you with?", "en", file="Athena/data/hello.mp3")
# Speak the mp3 file
playsound(os.getcwd() + '/Athena/data/hello.mp3', True)

# Run function.
chatbot()