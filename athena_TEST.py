import Athena.athena as ath

knowledge = ath.knowledge

# Check if user's name is known already.
if len(knowledge["user"]) == 0:
    ath.ask_name()
# Get the user's name
name = knowledge["user"][0]["name"]

print(f"Athena: Hello {name}, how are you doing?")

# Run function.
ath.chatbot()