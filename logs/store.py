import json
from datetime import datetime

def log_conversation(source, user_msg, bot_msg):
    log = {
        "time": datetime.now().isoformat(),
        "source": source,
        "user": user_msg,
        "bot": bot_msg
    }
    with open("logs/conversations.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")
