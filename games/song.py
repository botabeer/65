import random
from games.base import BaseGame
from config import Config

class SongGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الأغاني"
        self.songs = [
            {"lyric": "رجعت لي أيام الماضي معاك", "artist": ["ام كلثوم", "أم كلثوم"]},
            {"lyric": "الأطلال باقي الأطلال", "artist": ["ام كلثوم", "أم كلثوم"]},
            {"lyric": "هوا صحيح الهوى غلاب", "artist": ["ام كلثوم", "أم كلثوم"]},
            {"lyric": "قارئة الفنجان", "artist": ["عبدالحليم حافظ", "عبد الحليم حافظ"]},
            {"lyric": "على قد الشوق", "artist": ["عبدالحليم حافظ", "عبد الحليم حافظ"]},
            {"lyric": "أهواك وأتمنى لو أنساك", "artist": ["عبدالحليم حافظ", "عبد الحليم حافظ"]},
            {"lyric": "يا مسافر وحدك", "artist": ["فيروز"]},
            {"lyric": "سهار بعد سهار", "artist": ["فيروز"]},
            {"lyric": "زهرة المدائن", "artist": ["فيروز"]},
            {"lyric": "قولي يا طير الطاير", "artist": ["وردة", "وردة الجزائرية"]},
            {"lyric": "حبيب العمر", "artist": ["وردة", "وردة الجزائرية"]},
            {"lyric": "أنا مش عارفة ليه", "artist": ["نجاة الصغيرة"]},
            {"lyric": "هو صحيح الهوى غلاب", "artist": ["ام كلثوم", "أم كلثوم"]},
            {"lyric": "تعبت من الشوق", "artist": ["كاظم الساهر"]},
            {"lyric": "زيديني عشقا", "artist": ["كاظم الساهر"]},
            {"lyric": "قولي احبك", "artist": ["عمرو دياب"]},
            {"lyric": "تملي معاك", "artist": ["عمرو دياب"]},
            {"lyric": "حبيبي يا نور العين", "artist": ["عمرو دياب"]},
            {"lyric": "على بالي", "artist": ["محمد حماقي"]},
            {"lyric": "من قلبي بغني", "artist": ["محمد حماقي"]},
            {"lyric": "انا مش عارف اصبر", "artist": ["تامر حسني"]},
            {"lyric": "عيش بشوقك", "artist": ["تامر حسني"]},
            {"lyric": "يا مسهرني", "artist": ["عبدالمجيد عبدالله", "عبد المجيد عبد الله"]},
            {"lyric": "فوق هام السحب", "artist": ["عبدالمجيد عبدالله", "عبد المجيد عبد الله"]},
            {"lyric": "بعيد عنك", "artist": ["راشد الماجد"]},
            {"lyric": "عسى الله", "artist": ["راشد الماجد"]},
            {"lyric": "ما كنت أدري", "artist": ["نوال الكويتية"]},
            {"lyric": "يا ريتك معايا", "artist": ["شيرين"]},
            {"lyric": "مشاعر", "artist": ["شيرين"]},
            {"lyric": "بشرة خير", "artist": ["حسين الجسمي"]}
        ]
        random.shuffle(self.songs)
    
    def get_question(self):
        song = self.songs[self.current_q - 1]
        self.current_answer = song["artist"]
        
        question = f"من يغني:\n{song['lyric']}"
        hint = f"عدد الإجابات: {len(song['artist'])}"
        
        return self.build_question_flex(question, hint)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        return any(normalized == Config.normalize(artist) for artist in self.current_answer)
