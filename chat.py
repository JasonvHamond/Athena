# Import packages
import flet as ft
import Athena.athena as ath

# Message class
class Message():
    # Build the message
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

# ChatMessage c;ass
class ChatMessage(ft.Row):
    # Build the class
    def __init__(self, message: Message):
        super().__init__()
        # Align to start of page
        self.vertical_alignment="start"
        # Set the controls and styles.
        self.controls=[
                # Set Avatar Style
                ft.CircleAvatar(
                    # Get the initial of the username
                    content=ft.Text(self.get_initials(message.user_name)),
                    # Set text colour
                    color=ft.colors.WHITE,
                    # Find and set the background colour.
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                # Set message style
                ft.Column(
                    [
                        # Set Username
                        ft.Text(message.user_name, weight="bold"),
                        # Set the message.
                        ft.Text(message.text, selectable=True),
                    ],
                    tight=True,
                    spacing=5,
                ),
            ]

    # Get user's initials
    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "?"

    # Get the colours.
    def get_avatar_color(self, user_name: str):
        # Set list of colours
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        # Return the best fitted colour.
        return colors_lookup[hash(user_name) % len(colors_lookup)]

# Main function.
def main(page: ft.Page):
    # Set the alignment of the page
    page.horizontal_alignment = "stretch"
    # Set page title.
    page.title = "Athena"
    answer_ath = ""

    # Join the chat.
    def join_chat_click(e):
        # Check if a name had been filled in.
        if not join_user_name.value:
            # Give error message
            join_user_name.error_text = "Please enter a valid name."
            join_user_name.update()
        # If name is filled.
        else:
            # Set the username
            page.session.set("user_name", join_user_name.value)
            page.dialog.open = False
            # Set the new message for joining user.
            new_message.prefix = ft.Text(f"{join_user_name.value}: ")
            # Send the welcome message.
            page.pubsub.send_all(Message(user_name=join_user_name.value, text=f"{join_user_name.value} has joined the chat.", message_type="login_message"))
            page.update()

    # When message is sent.
    def answer_athena(e):
        # If t he message is not empty
        if new_message.value != "":
            # Send the message
            page.pubsub.send_all(Message(page.session.get("user_name"), new_message.value, message_type="chat_message"))
            page.update()

    def athena_response(user_input: str):
        knowledge = ath.knowledge
        match = ath.find_match(user_input, [question["question"] for question in knowledge["questions"]])
        ### WIP ###
        if("tell me a joke" in user_input.lower()):
            # ath.tell_joke()
            return
        elif(match):
            answer = ath.get_answer(match, knowledge)
            page.pubsub.send_all(Message("Athena", answer, message_type="chat_message"))
            page.update()
        else:
            # Ask question.
            ath_question = "What would you like me to answer with?"
            page.pubsub.send_all(Message("Athena", ath_question, message_type="chat_message"))
            page.update()
            # Get user answer

            new_message.value = ""
            new_message.focus()
            page.update()

            ### NEEDS FIXES ###
            new_message = ft.TextField(
                hint_text="Write a message...",
                autofocus=True,
                shift_enter=True,
                min_lines=1,
                max_lines=5,
                filled=True,
                expand=True,
                on_submit=answer_athena,
            )

            if(new_message.value.lower() != "skip"):
                knowledge["questions"].append({"question": user_input, "answer": new_message.value})
                ath.save_knowledge("data/knowledge.json", knowledge)
                # Reset message value
                new_message.value = ""
                new_message.focus()
                page.update()
                # Write response for Athena.
                athena_response = "I will keep this in mind."
                page.pubsub.send_all(Message("Athena", athena_response.value, message_type="chat_message"))
                page.update()

    # When message is sent.
    def send_message_click(e):
        # If t he message is not empty
        if new_message.value != "":
            # Send the message
            page.pubsub.send_all(Message(page.session.get("user_name"), new_message.value, message_type="chat_message"))
            page.update()
            # Let athena respond
            athena_response(new_message.value)
            # Reset message value
            new_message.value = ""
            new_message.focus()
            page.update()

    # On message function
    def on_message(message: Message):
        # Check message type
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        # If message type is login message
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.GREEN_200, size=12)
        chat.controls.append(m)
        page.update()
    # set message.
    page.pubsub.subscribe(on_message)

    # Ask for the username
    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
    )
    # Show dialogue to enter username
    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        # Show Welcome title
        title=ft.Text("Welcome!"),
        # Let user enter a name
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        # If clicked, welcome the user.
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment="end",
    )

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Enter a new message.
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    # Add all the things to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )

# Start functions
ft.app(port=8550, target=main, view=ft.WEB_BROWSER)