"""
Bot 65 - Games Engine
جميع الألعاب في ملف واحد
"""
import random
import re
from datetime import datetime
from linebot.v3.messaging import TextMessage


def norm(text):
    """تطبيع النص العربي"""
    if not text:
        return ""
    text = text.strip().lower()
    for old, new in {'أ':'ا','إ':'ا','آ':'ا','ؤ':'و','ئ':'ي','ء':'','ة':'ه','ى':'ي'}.items():
        text = text.replace(old, new)
    return re.sub(r'[\u064B-\u065F\u0670]', '', text)


class BaseGame:
    """كلاس أساسي للألعاب"""
    def __init__(self, theme='light'):
        self.theme = theme
        self.name = "لعبة"
        self.total = 5
        self.current = 0
        self.answer = None
        self.scores = {}
        self.answered = set()
        self.active = False
        self.start_time = None
    
    def start(self):
        """بدء اللعبة"""
        self.current = 0
        self.scores.clear()
        self.answered.clear()
        self.active = True
        self.start_time = datetime.now()
        return self.question()
    
    def question(self):
        """السؤال - يجب تنفيذه"""
        raise NotImplementedError
    
    def play(self, text, uid, name):
        """معالجة الإجابة"""
        if not self.active or uid in self.answered:
            return {}
        
        t = norm(text)
        
        # تلميح
        if t in ['لمح', 'تلميح']:
            return {'response': TextMessage(text=self.hint())}
        
        # إظهار الجواب
        if t in ['جاوب', 'الجواب', 'الحل']:
            self.current += 1
            self.answered.clear()
            if self.current >= self.total:
                return self.end()
            return {'response': TextMessage(text=f"الجواب: {self.answer}"), 'next': True}
        
        # التحقق
        if self.check(t):
            if uid not in self.scores:
                self.scores[uid] = {'name': name, 'score': 0}
            self.scores[uid]['score'] += 1
            self.answered.add(uid)
            self.current += 1
            
            if self.current >= self.total:
                return self.end()
            
            return {'response': TextMessage(text=f"صحيح +1\n\n{self.question().text}")}
        
        return {}
    
    def check(self, text):
        """التحقق من الإجابة - يجب تنفيذه"""
        raise NotImplementedError
    
    def hint(self):
        """التلميح"""
        return f"يبدأ بـ: {self.answer[0]}\nعدد الحروف: {len(self.answer)}"
    
    def end(self):
        """نهاية اللعبة"""
        self.active = False
        if not self.scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'game_over': True, 'points': 0}
        
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_scores[0][1]
        
        msg = f"انتهت {self.name}\n\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        if len(sorted_scores) > 1:
            msg += "\n\nالترتيب:\n"
            for i, (_, d) in enumerate(sorted_scores[:5], 1):
                msg += f"{i}. {d['name']} - {d['score']}\n"
        
        return {'response': TextMessage(text=msg), 'game_over': True, 'points': winner['score'], 'won': True}


# === الألعاب ===

class SongGame(BaseGame):
    """لعبة الأغاني"""
    DATA = [
        {"l": "رجعت لي أيام الماضي معاك", "a": "أم كلثوم"},
        {"l": "قولي أحبك كي تزيد وسامتي", "a": "كاظم الساهر"},
        {"l": "جلست والخوف بعينيها تتأمل فنجاني", "a": "عبد الحليم حافظ"},
        {"l": "تملي معاك ولو حتى بعيد عني", "a": "عمرو دياب"},
        {"l": "يا بنات يا بنات", "a": "نانسي عجرم"},
        {"l": "قلبي بيسألني عنك", "a": "وائل كفوري"},
        {"l": "حبيبي يا كل الحياة", "a": "تامر حسني"},
        {"l": "كيف أبيّن لك شعوري", "a": "عايض"},
    ]
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "أغنية"
        self.items = random.sample(self.DATA, min(self.total, len(self.DATA)))
    
    def question(self):
        q = self.items[self.current]
        self.answer = q['a']
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\n{q['l']}\n\nمن المغني؟")
    
    def check(self, text):
        return norm(text) == norm(self.answer)


class OppositeGame(BaseGame):
    """لعبة الأضداد"""
    DATA = {
        'كبير': 'صغير', 'طويل': 'قصير', 'سريع': 'بطيء',
        'ساخن': 'بارد', 'نظيف': 'وسخ', 'جديد': 'قديم',
        'صعب': 'سهل', 'قوي': 'ضعيف', 'غني': 'فقير',
        'سعيد': 'حزين', 'جميل': 'قبيح', 'ثقيل': 'خفيف'
    }
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "أضداد"
        self.items = random.sample(list(self.DATA.items()), self.total)
    
    def question(self):
        word, opposite = self.items[self.current]
        self.answer = opposite
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\nما عكس:\n{word}")
    
    def check(self, text):
        return norm(text) == norm(self.answer)


class ChainGame(BaseGame):
    """لعبة السلسلة"""
    WORDS = ['سيارة','كتاب','قلم','باب','نافذة','طاولة','كرسي','حديقة','شجرة','زهرة']
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "سلسلة"
        self.last = random.choice(self.WORDS)
        self.used = {norm(self.last)}
    
    def question(self):
        letter = self.last[-1]
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\nالكلمة: {self.last}\nابدأ بحرف: {letter}")
    
    def check(self, text):
        n = norm(text)
        if n in self.used or len(n) < 2:
            return False
        if n[0] == norm(self.last[-1]):
            self.used.add(n)
            self.last = text.strip()
            return True
        return False


class FastTypingGame(BaseGame):
    """لعبة الكتابة السريعة"""
    DATA = ['سبحان الله','الحمد لله','لا إله إلا الله','الله أكبر','استغفر الله']
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "كتابة سريعة"
        self.items = random.choices(self.DATA, k=self.total)
    
    def question(self):
        phrase = self.items[self.current]
        self.answer = phrase
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\nاكتب:\n{phrase}")
    
    def check(self, text):
        return text.strip() == self.answer


class HumanAnimalGame(BaseGame):
    """لعبة إنسان حيوان نبات"""
    DATA = {
        'إنسان': {'م': ['محمد','مريم'], 'أ': ['أحمد','أمل'], 'ع': ['علي','عمر']},
        'حيوان': {'أ': ['أسد','أرنب'], 'ج': ['جمل'], 'ف': ['فيل','فهد']},
        'نبات': {'ت': ['تفاح','تمر'], 'ب': ['بطيخ','برتقال'], 'ع': ['عنب']},
        'جماد': {'ب': ['باب','بيت'], 'ك': ['كرسي','كتاب'], 'ق': ['قلم']},
        'بلاد': {'أ': ['أمريكا'], 'س': ['السعودية','سوريا'], 'م': ['مصر']}
    }
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "إنسان حيوان"
        self.cats = list(self.DATA.keys())
    
    def question(self):
        cat = random.choice(self.cats)
        letter = random.choice(list(self.DATA[cat].keys()))
        self.cat = cat
        self.letter = letter
        self.answer = self.DATA[cat][letter][0]
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\nالفئة: {cat}\nالحرف: {letter}")
    
    def check(self, text):
        n = norm(text)
        if n and n[0] == norm(self.letter):
            return True
        return False


class LettersGame(BaseGame):
    """لعبة تكوين الكلمات"""
    DATA = [
        {'letters': ['ق','ل','م','ع','ر'], 'words': ['قلم','علم','عمر']},
        {'letters': ['ك','ت','ا','ب','م'], 'words': ['كتاب','كتب','مكتب']},
        {'letters': ['د','ر','س','ة','م'], 'words': ['مدرسة','درس']},
    ]
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "تكوين كلمات"
        self.items = random.sample(self.DATA, min(self.total, len(self.DATA)))
        self.found = set()
        self.required = 2
    
    def question(self):
        item = self.items[self.current]
        self.words = [norm(w) for w in item['words']]
        self.found.clear()
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\nالحروف: {' '.join(item['letters'])}\n\nكوّن {self.required} كلمات")
    
    def check(self, text):
        n = norm(text)
        if n in self.words and n not in self.found:
            self.found.add(n)
            if len(self.found) >= self.required:
                return True
        return False


class CategoryGame(BaseGame):
    """لعبة الفئة والحرف"""
    DATA = [
        {'cat': 'المطبخ', 'letter': 'ق', 'answers': ['قدر','قلاية']},
        {'cat': 'حيوان', 'letter': 'ب', 'answers': ['بطة','بقرة']},
        {'cat': 'فاكهة', 'letter': 'ت', 'answers': ['تفاح','توت','تمر']},
        {'cat': 'خضار', 'letter': 'ب', 'answers': ['بصل','بطاطس']},
        {'cat': 'بلاد', 'letter': 'س', 'answers': ['السعودية','سوريا']},
    ]
    
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "فئة"
        self.items = random.sample(self.DATA, min(self.total, len(self.DATA)))
    
    def question(self):
        item = self.items[self.current]
        self.answers = [norm(a) for a in item['answers']]
        return TextMessage(text=f"{self.name} {self.current+1}/{self.total}\n\nالفئة: {item['cat']}\nالحرف: {item['letter']}")
    
    def check(self, text):
        return norm(text) in self.answers


class CompatibilityGame(BaseGame):
    """لعبة التوافق"""
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "توافق"
        self.total = 1
    
    def question(self):
        return TextMessage(text=f"{self.name}\n\nاكتب اسمين مع (و) بينهما\nمثال: احمد و سارة")
    
    def play(self, text, uid, name):
        if 'و' not in text:
            return {}
        
        parts = text.replace(' و ', '|').split('|')
        if len(parts) != 2:
            return {}
        
        n1, n2 = parts[0].strip(), parts[1].strip()
        if not n1 or not n2:
            return {}
        
        # حساب النسبة
        seed = sum(ord(c) for c in norm(n1 + n2))
        percentage = (seed % 81) + 20
        
        msg = f"نسبة التوافق\n\n{n1} و {n2}\n\n{percentage}%"
        if percentage >= 80:
            msg += "\nتوافق ممتاز"
        elif percentage >= 60:
            msg += "\nتوافق جيد"
        else:
            msg += "\nتوافق متوسط"
        
        return {'response': TextMessage(text=msg), 'game_over': True, 'points': 0}
    
    def check(self, text):
        return False


# === محرك الألعاب ===

class GameEngine:
    """محرك إنشاء الألعاب"""
    
    GAMES = {
        'اغنيه': SongGame,
        'ضد': OppositeGame,
        'سلسله': ChainGame,
        'اسرع': FastTypingGame,
        'لعبه': HumanAnimalGame,
        'تكوين': LettersGame,
        'فئه': CategoryGame,
        'توافق': CompatibilityGame
    }
    
    @staticmethod
    def create(game_cmd, theme='light'):
        """إنشاء لعبة"""
        game_class = GameEngine.GAMES.get(game_cmd)
        return game_class(theme) if game_class else None
