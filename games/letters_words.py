import random
from games.base import BaseGame
from config import Config

class LettersWordsGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة تكوين الكلمات"
        self.supports_reveal = False
        self.required_words = 3
        self.found_words = []
        self.letter_sets = [
            {"letters": "ق ل م ع ر ب", "words": ["قلم", "علم", "قمر", "عرب", "رمل"]},
            {"letters": "ك ت ا ب و ر", "words": ["كتاب", "باب", "كات", "روب", "بار"]},
            {"letters": "م ن ز ل د ي", "words": ["منزل", "يد", "دين", "ديم", "زين"]},
            {"letters": "ش م س ع ن د", "words": ["شمس", "عند", "سند", "شعد", "نعم"]},
            {"letters": "ب ح ر ي ت ك", "words": ["بحر", "بيت", "حبر", "بكر", "كبير"]}
        ]
    
    def get_question(self):
        letter_set = random.choice(self.letter_sets)
        self.current_answer = letter_set["words"]
        self.found_words = []
        
        question = f"كون {self.required_words} كلمات من الأحرف:\n{letter_set['letters']}\n\nأرسل كلمة واحدة في كل مرة"
        hint = f"الكلمات الممكنة: {len(letter_set['words'])}"
        
        return self.build_question_flex(question, hint)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        
        if normalized in [Config.normalize(w) for w in self.found_words]:
            return False
        
        if any(normalized == Config.normalize(word) for word in self.current_answer):
            self.found_words.append(answer)
            return len(self.found_words) >= self.required_words
        
        return False
