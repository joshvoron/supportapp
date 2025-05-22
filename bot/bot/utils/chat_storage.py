import json
import os

CHAT_FILE = "utils/chat_storage.json"


class ChatStorage:
    def __init__(self, file_path=CHAT_FILE):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"chats": []}, f)

    def add_chat(self, chat_id, telegram_id):
        chats = self.get_all_chats()
        data = {
            "id": chat_id,
            "user_id": telegram_id,
            "is_solved": False
        }
        if chat_id not in chats:
            chats.append(data)
            self._save_chats(chats)

    def remove_chat(self, chat_id):
        chats = self.get_all_chats()
        if chat_id in chats:
            chats.remove(chat_id)
            self._save_chats(chats)

    def find_chat(self, telegram_id):
        chats = self.get_all_chats()
        for chat in chats:
            if chat.get('user_id') == telegram_id and chat.get('is_solved') is False:
                return chat
        return None

    def get_all_chats(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)
        return data.get("chats", [])

    def _save_chats(self, chats):
        with open(self.file_path, "w") as f:
            json.dump({"chats": chats}, f, indent=4)

    def chat_exists(self, chat_id):
        return chat_id in self.get_all_chats()
