import random
import os

class TextManager:
    def __init__(self):
        self.base_path = "games"
        self.challenges = self._load_file("challenges.txt")
        self.confessions = self._load_file("confessions.txt")
        self.mentions = self._load_file("mentions.txt")
        self.personality = self._load_file("personality.txt")
        self.questions = self._load_file("questions.txt")
        self.quotes = self._load_file("quotes.txt")
        self.situations = self._load_file("situations.txt")
        
        self.cmd_mapping = {
            "تحدي": self.challenges,
            "اعتراف": self.confessions,
            "منشن": self.mentions,
            "شخصيه": self.personality,
            "شخصية": self.personality,
            "سؤال": self.questions,
            "حكمه": self.quotes,
            "حكمة": self.quotes,
            "موقف": self.situations
        }
    
    def _load_file(self, filename):
        path = os.path.join(self.base_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                return lines if lines else ["المحتوى غير متوفر"]
        except:
            return ["المحتوى غير متوفر"]
    
    def get_content(self, cmd):
        content_list = self.cmd_mapping.get(cmd)
        if content_list:
            return random.choice(content_list)
        return None
