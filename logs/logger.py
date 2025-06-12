def log_interaction(user_message: str, response: str):
    with open("logs/samples/chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"User: {user_message}\nBot: {response}\n\n")
