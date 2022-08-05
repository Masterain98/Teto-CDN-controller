import json
import requests


class TgMsg:
    def __init__(self, first_message: str = None):
        if first_message is None:
            self.message_list = []
        else:
            self.message_list = [first_message]
        with open("./config/telegram.json", "r") as f:
            config = json.load(f)
        self.TG_USER_ID = config["TG_USER_ID"]
        self.TG_BOT_API = config["TG_BOT_API"] + config["TG_BOT_TOKEN"]

    def add_message(self, message: str):
        self.message_list.append(message)
        print(message)

    def get_message(self):
        return self.message_list

    def push(self):
        msg = "\n".join(self.message_list)
        data = {"text": msg, "chat_id": self.TG_USER_ID}
        request_result = requests.post(url=self.TG_BOT_API + "/sendMessage", data=data)
        if request_result.status_code:
            print("Telegram message sent successfully")
            return True
        else:
            print("Telegram message sent failed: " + str(request_result.text))
            return False
