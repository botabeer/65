import random
from linebot.v3.messaging import FlexMessage, FlexContainer

class GameEngine:
    GAMES = {
        'اغنيه': 'song', 'ضد': 'opposite', 'سلسله': 'chain',
        'اسرع': 'fast', 'تكوين': 'letters', 'فئه': 'category',
        'لعبه': 'human', 'توافق': 'compat', 'ذكاء': 'iq',
        'خمن': 'guess', 'ترتيب': 'scramble', 'لون': 'color',
        'روليت': 'roulette', 'سين': 'seenjeem', 'حروف': 'letter',
        'مافيا': 'mafia'
    }
    
    @staticmethod
    def create(game_type, theme='light'):
        game_map = {
            'song': SongG, 'opposite': OppositeG, 'chain': ChainG,
            'fast': FastG, 'letters': LettersG, 'category': CategoryG,
            'human': HumanG, 'compat': CompatG, 'iq': IqG,
            'guess': GuessG, 'scramble': ScrambleG, 'color': ColorG,
            'roulette': RouletteG, 'seenjeem': SeenJeemG, 'letter': LetterG,
            'mafia': MafiaG
        }
        gtype = GameEngine.GAMES.get(game_type)
        return game_map[gtype](theme) if gtype in game_map else None

class BaseG:
    def __init__(self, theme='light'):
        self.theme = theme
        self.q = 5
        self.i = 0
        self.s = 0
        self.ans = None
        self.name = "لعبة"
        
    def c(self):
        t = {"light":{"p":"#2563EB","s":"#10B981","w":"#F59E0B","e":"#EF4444",
                     "t":"#1F2937","t2":"#6B7280","bg":"#FFF","c":"#F9FAFB","b":"#E5E7EB"},
             "dark":{"p":"#3B82F6","s":"#34D399","w":"#FBBF24","e":"#F87171",
                    "t":"#F9FAFB","t2":"#D1D5DB","bg":"#1F2937","c":"#374151","b":"#4B5563"}}
        return t.get(self.theme, t["light"])
    
    def norm(self, txt):
        if not txt: return ""
        txt = txt.strip().lower()
        for o,n in [('أ','ا'),('إ','ا'),('آ','ا'),('ؤ','و'),('ئ','ي'),('ء',''),('ة','ه'),('ى','ي')]:
            txt = txt.replace(o, n)
        import re
        return re.sub(r'[\u064B-\u065F\u0670]', '', txt).strip()
    
    def flex(self, q, h=None):
        c = self.c()
        cnt = [
            {"type":"text","text":self.name,"size":"xl","weight":"bold","color":c["p"],"align":"center"},
            {"type":"separator","margin":"md","color":c["b"]},
            {"type":"box","layout":"baseline","contents":[
                {"type":"text","text":f"{self.i+1}","size":"sm","color":c["t2"],"flex":0},
                {"type":"text","text":f"من {self.q}","size":"sm","color":c["t2"],"align":"end","flex":1}
            ],"margin":"md"},
            {"type":"separator","margin":"md","color":c["b"]},
            {"type":"text","text":q,"size":"md","color":c["t"],"wrap":True,"margin":"lg","align":"center"}
        ]
        if h:
            cnt.append({"type":"text","text":h,"size":"xs","color":c["t2"],"wrap":True,"margin":"sm","align":"center"})
        cnt.extend([
            {"type":"separator","margin":"lg","color":c["b"]},
            {"type":"box","layout":"horizontal","contents":[
                {"type":"button","action":{"type":"message","label":"تلميح","text":"لمح"},"style":"secondary","height":"sm"},
                {"type":"button","action":{"type":"message","label":"الاجابة","text":"جاوب"},"style":"secondary","height":"sm","color":c["w"]},
                {"type":"button","action":{"type":"message","label":"انسحب","text":"انسحب"},"style":"secondary","height":"sm","color":c["e"]}
            ],"spacing":"sm","margin":"md"}
        ])
        return FlexMessage(alt_text=self.name, contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":cnt,
            "backgroundColor":c["bg"],"paddingAll":"20px"}
        }))
    
    def start(self):
        self.i = 0
        self.s = 0
        return self.get_q()
    
    def play(self, txt, uid, name):
        n = self.norm(txt)
        if n == "لمح": return self.hint()
        if n == "جاوب": return self.reveal()
        
        if self.check(n):
            self.s += 1
            self.i += 1
            if self.i >= self.q:
                return {'game_over':True,'points':self.s,'won':True,'response':self.res()}
            return {'response':self.get_q(),'points':1}
        return {}
    
    def hint(self):
        if not self.ans: return {}
        a = self.ans[0] if isinstance(self.ans, list) else self.ans
        from linebot.v3.messaging import TextMessage
        return {'response':TextMessage(text=f"يبدأ بـ: {a[0]}\nعدد الحروف: {len(a)}")}
    
    def reveal(self):
        if not self.ans: return {}
        a = ' او '.join(self.ans) if isinstance(self.ans, list) else self.ans
        self.i += 1
        if self.i >= self.q:
            return {'game_over':True,'points':self.s,'response':self.res()}
        from linebot.v3.messaging import TextMessage
        return {'response':TextMessage(text=f"الاجابة: {a}")}
    
    def res(self):
        c = self.c()
        from linebot.v3.messaging import TextMessage
        return TextMessage(text=f"انتهت اللعبة\nالنقاط: {self.s}/{self.q}")

class SongG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "اغنيه"
        self.data = [
            {"l":"رجعت لي أيام الماضي معاك","a":"أم كلثوم"},
            {"l":"قولي أحبك كي تزيد وسامتي","a":"كاظم الساهر"},
            {"l":"بردان أنا تكفى أبي احترق بدفا لعيونك","a":"محمد عبده"},
            {"l":"جلست والخوف بعينيها تتأمل فنجاني","a":"عبد الحليم حافظ"},
            {"l":"أحبك موت كلمة مالها تفسير","a":"ماجد المهندس"},
            {"l":"تملي معاك ولو حتى بعيد عني","a":"عمرو دياب"},
            {"l":"يا بنات يا بنات","a":"نانسي عجرم"},
            {"l":"رحت عني ما قويت جيت لك لاتردني","a":"عبدالمجيد عبدالله"}
        ]
        random.shuffle(self.data)
    
    def get_q(self):
        d = self.data[self.i % len(self.data)]
        self.ans = [d["a"]]
        return self.flex(d["l"], "من المغني؟")
    
    def check(self, txt):
        return any(self.norm(a) == txt for a in self.ans)

class OppositeG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "ضد"
        self.data = {'كبير':['صغير'],'طويل':['قصير'],'سريع':['بطيء'],
                    'ساخن':['بارد'],'نظيف':['وسخ'],'جديد':['قديم'],
                    'صعب':['سهل'],'قوي':['ضعيف'],'غني':['فقير'],
                    'سعيد':['حزين'],'جميل':['قبيح'],'ثقيل':['خفيف']}
        self.lst = list(self.data.items())
        random.shuffle(self.lst)
    
    def get_q(self):
        w, a = self.lst[self.i % len(self.lst)]
        self.ans = a
        return self.flex(f"ما عكس كلمة:\n{w}")
    
    def check(self, txt):
        return any(self.norm(a) == txt for a in self.ans)

class ChainG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "سلسله"
        self.words = ['سيارة','تفاح','قلم','نجم','كتاب','باب','رمل',
                     'لعبة','حديقة','ورد','دفتر','معلم','منزل','شمس']
        self.last = random.choice(self.words)
        self.used = {self.norm(self.last)}
    
    def get_q(self):
        return self.flex(f"الكلمة السابقة: {self.last}", f"ابدأ بحرف: {self.last[-1]}")
    
    def check(self, txt):
        n = self.norm(txt)
        if n in self.used or not n or len(n) < 2:
            return False
        if n[0] == self.norm(self.last[-1]):
            self.used.add(n)
            self.last = txt.strip()
            return True
        return False

class FastG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "اسرع"
        self.phrases = ['سبحان الله','الحمد لله','الله أكبر','لا إله إلا الله',
                       'استغفر الله','لا حول ولا قوة إلا بالله']
        random.shuffle(self.phrases)
    
    def get_q(self):
        self.ans = self.phrases[self.i % len(self.phrases)]
        return self.flex(self.ans, "اكتب النص بالضبط")
    
    def check(self, txt):
        return txt.strip() == self.ans

class LettersG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "تكوين"
        self.data = [
            {'l':['ق','ل','م','ع','ر','ب'],'w':['قلم','علم','عمر','رقم']},
            {'l':['ك','ت','ا','ب','م','ل'],'w':['كتاب','كتب','مكتب','ملك']},
            {'l':['د','ر','س','ة','م','ا'],'w':['مدرسة','درس','مدرس']},
            {'l':['ح','د','ي','ق','ة','ر'],'w':['حديقة','حديد','قرد']}
        ]
        random.shuffle(self.data)
        self.found = set()
        self.need = 3
    
    def get_q(self):
        d = self.data[self.i % len(self.data)]
        self.ans = d['w']
        self.found = set()
        return self.flex(f"كون كلمات من:\n{' '.join(d['l'])}", f"مطلوب {self.need} كلمات")
    
    def check(self, txt):
        n = self.norm(txt)
        valid = [self.norm(w) for w in self.ans]
        if n in valid and n not in self.found:
            self.found.add(n)
            return len(self.found) >= self.need
        return False

class CategoryG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "فئه"
        self.data = [
            {'c':'المطبخ','l':'ق','a':['قدر','قلاية']},
            {'c':'حيوان','l':'ب','a':['بطة','بقرة','ببغاء']},
            {'c':'فاكهة','l':'ت','a':['تفاح','توت','تمر']},
            {'c':'خضار','l':'ب','a':['بصل','بطاطس','باذنجان']},
            {'c':'بلاد','l':'س','a':['سعودية','سوريا','سودان']}
        ]
        random.shuffle(self.data)
    
    def get_q(self):
        d = self.data[self.i % len(self.data)]
        self.ans = d['a']
        return self.flex(f"الفئة: {d['c']}\nالحرف: {d['l']}")
    
    def check(self, txt):
        return any(self.norm(a) == self.norm(txt) for a in self.ans)

class HumanG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "لعبه"
        self.letters = list("ابتجحدرزسشصطعفقكلمنهوي")
        random.shuffle(self.letters)
        self.cats = ["إنسان","حيوان","نبات","جماد","بلاد"]
    
    def get_q(self):
        self.letter = self.letters[self.i % len(self.letters)]
        self.cat = random.choice(self.cats)
        return self.flex(f"الفئة: {self.cat}\nالحرف: {self.letter}")
    
    def check(self, txt):
        n = self.norm(txt)
        return n and len(n) >= 2 and n[0] == self.norm(self.letter)

class CompatG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "توافق"
        self.q = 1
    
    def get_q(self):
        from linebot.v3.messaging import TextMessage
        return TextMessage(text="اكتب اسمين مع (و) بينهما\nمثال: احمد و سارة")
    
    def play(self, txt, uid, name):
        if ' و ' not in txt and 'و' not in txt:
            return {}
        parts = txt.replace(' و ',' ').replace('و',' ').split()
        if len(parts) < 2:
            return {}
        n1, n2 = parts[0].strip(), parts[1].strip()
        if not n1 or not n2:
            return {}
        seed = sum(ord(c) for c in (n1+n2))
        random.seed(seed)
        pct = random.randint(20, 100)
        msg = "ممتاز" if pct >= 90 else "جيد" if pct >= 60 else "متوسط"
        from linebot.v3.messaging import TextMessage
        return {'game_over':True,'points':0,'response':TextMessage(
            text=f"نسبة التوافق\n\n{n1} و {n2}\n\nالنسبة: {pct}%\n{msg}")}
    
    def check(self, txt):
        return False

class IqG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "ذكاء"
        self.data = [
            {"q":"ما الشيء الذي يمشي بلا أرجل ويبكي بلا عيون","a":["السحاب","الغيم"]},
            {"q":"له رأس ولكن لا عين له","a":["الدبوس","المسمار","الإبرة"]},
            {"q":"شيء كلما زاد نقص","a":["العمر","الوقت"]},
            {"q":"يكتب ولا يقرأ أبدا","a":["القلم"]},
            {"q":"له أسنان كثيرة ولكنه لا يعض","a":["المشط"]}
        ]
        random.shuffle(self.data)
    
    def get_q(self):
        d = self.data[self.i % len(self.data)]
        self.ans = d['a']
        return self.flex(d['q'])
    
    def check(self, txt):
        return any(self.norm(a) == txt for a in self.ans)

class GuessG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "خمن"
        self.data = {
            "المطبخ":{"ق":["قدر","قلاية"],"م":["ملعقة","مغرفة"]},
            "غرفة النوم":{"س":["سرير","ستارة"],"و":["وسادة"]},
            "المدرسة":{"ق":["قلم"],"د":["دفتر"],"ك":["كتاب"]},
            "الفواكه":{"ت":["تفاح","تمر"],"م":["موز"],"ع":["عنب"]},
            "الحيوانات":{"ق":["قطة"],"ف":["فيل"],"أ":["أسد","أرنب"]}
        }
        self.lst = []
        for cat, lets in self.data.items():
            for let, words in lets.items():
                self.lst.append({'c':cat,'l':let,'a':words})
        random.shuffle(self.lst)
    
    def get_q(self):
        d = self.lst[self.i % len(self.lst)]
        self.ans = d['a']
        return self.flex(f"الفئة: {d['c']}\nيبدأ بحرف: {d['l']}")
    
    def check(self, txt):
        return any(self.norm(a) == txt for a in self.ans)

class ScrambleG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "ترتيب"
        self.words = ['مدرسة','كتاب','قلم','باب','نافذة','طاولة','كرسي',
                     'سيارة','طائرة','قطار','تفاحة','موز','برتقال']
        random.shuffle(self.words)
    
    def get_q(self):
        w = self.words[self.i % len(self.words)]
        self.ans = w
        letters = list(w)
        for _ in range(10):
            random.shuffle(letters)
            if ''.join(letters) != w:
                break
        return self.flex(f"رتب الحروف:\n{' '.join(letters)}", f"عدد الحروف: {len(w)}")
    
    def check(self, txt):
        return self.norm(txt) == self.norm(self.ans)

class ColorG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "لون"
        self.colors = ["أحمر","أزرق","أخضر","أصفر","برتقالي","بنفسجي"]
    
    def get_q(self):
        word = random.choice(self.colors)
        color = random.choice([c for c in self.colors if c != word]) if random.random() < 0.7 else word
        self.ans = [color]
        return self.flex(f"ما لون هذه الكلمة:\n\n{word}\n\nملاحظة: اللون مكتوب باللون {color}")
    
    def check(self, txt):
        return any(self.norm(a) == txt for a in self.ans)

class RouletteG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "روليت"
        self.nums = list(range(0, 37))
        self.red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        self.black = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
    
    def get_q(self):
        self.num = random.choice(self.nums)
        clr = "أخضر" if self.num == 0 else ("أحمر" if self.num in self.red else "أسود")
        from linebot.v3.messaging import TextMessage
        return TextMessage(text=f"تدور الروليت\n\nالرقم: {self.num}\nاللون: {clr}\n\nخيارات: رقم (0-36) | لون (احمر/اسود) | زوجي/فردي")
    
    def check(self, txt):
        try:
            return int(txt.strip()) == self.num
        except:
            clr = "أخضر" if self.num == 0 else ("أحمر" if self.num in self.red else "أسود")
            n = self.norm(txt)
            if (n == "احمر" and clr == "أحمر") or (n == "اسود" and clr == "أسود"):
                return True
            if self.num != 0:
                even = self.num % 2 == 0
                if (n == "زوجي" and even) or (n == "فردي" and not even):
                    return True
        return False

class SeenJeemG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "سين"
        self.data = [
            {"q":"ما هو الشيء الذي يمشي بلا رجلين ويبكي بلا عينين","a":"السحاب"},
            {"q":"ما هو الشيء الذي له اسنان ولا يعض","a":"المشط"},
            {"q":"ما هو الشيء الذي كلما زاد نقص","a":"العمر"},
            {"q":"ما اطول نهر في العالم","a":"النيل"},
            {"q":"ما هي عاصمة السعودية","a":"الرياض"}
        ]
        random.shuffle(self.data)
    
    def get_q(self):
        d = self.data[self.i % len(self.data)]
        self.ans = [d['a']]
        return self.flex(d['q'])
    
    def check(self, txt):
        return any(self.norm(a) in txt or txt in self.norm(a) for a in self.ans)

class LetterG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "حروف"
        self.letters = {'ا':['ادم','الجزائر'],'ب':['بغداد','بكين'],'ت':['تونس','تايبيه'],
                       'ج':['جيبوتي','جدة'],'ح':['حلب','حماة'],'د':['دبلن','دمشق']}
        self.lst = list(self.letters.keys())
        random.shuffle(self.lst)
    
    def get_q(self):
        self.let = self.lst[self.i % len(self.lst)]
        return self.flex(f"حرف:\n\n{self.let}\n\nاكتب كلمة تبدأ بهذا الحرف")
    
    def check(self, txt):
        n = self.norm(txt)
        return n and n[0] == self.norm(self.let)

class MafiaG(BaseG):
    def __init__(self, theme='light'):
        super().__init__(theme)
        self.name = "مافيا"
        self.q = 1
        self.phase = "wait"
        self.players = {}
        self.roles = {}
        self.alive = set()
        self.mafia = set()
        self.min_p = 4
    
    def get_q(self):
        c = self.c()
        cnt = [
            {"type":"text","text":"لعبة المافيا","size":"xxl","weight":"bold","color":c["p"],"align":"center"},
            {"type":"separator","margin":"lg","color":c["b"]},
            {"type":"text","text":"شرح اللعبة","size":"md","weight":"bold","color":c["t"],"align":"center"},
            {"type":"text","text":"مافيا يحاولون قتل المدنيين\nمدنيين يصوتون لطرد المشتبهين","size":"xs","color":c["t2"],"wrap":True,"margin":"sm"},
            {"type":"separator","margin":"md","color":c["b"]},
            {"type":"text","text":f"اللاعبون: {len(self.players)}/{20}","size":"sm","color":c["t"],"align":"center","margin":"md"},
            {"type":"text","text":f"الحد الادنى: {self.min_p} لاعبين","size":"xs","color":c["t2"],"align":"center","margin":"xs"},
            {"type":"separator","margin":"md","color":c["b"]},
            {"type":"text","text":"اكتب 'انضم' للانضمام\nاكتب 'ابدأ' لبدء اللعبة","size":"sm","color":c["t2"],"align":"center","wrap":True,"margin":"md"}
        ]
        return FlexMessage(alt_text=self.name, contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":cnt,
            "backgroundColor":c["bg"],"paddingAll":"20px"}
        }))
    
    def play(self, txt, uid, name):
        n = self.norm(txt)
        if self.phase == "wait":
            if n in ["انضم","join"]:
                if uid not in self.players and len(self.players) < 20:
                    self.players[uid] = name
                    from linebot.v3.messaging import TextMessage
                    return {'response':TextMessage(text=f"{name} انضم - العدد: {len(self.players)}")}
            elif n in ["ابدأ","start","بدا"]:
                if len(self.players) >= self.min_p:
                    self._assign_roles()
                    self.phase = "night"
                    from linebot.v3.messaging import TextMessage
                    return {'response':TextMessage(text="بدأت اللعبة")}
                else:
                    from linebot.v3.messaging import TextMessage
                    return {'response':TextMessage(text=f"يحتاج {self.min_p-len(self.players)} لاعبين")}
        return {}
    
    def _assign_roles(self):
        plist = list(self.players.keys())
        random.shuffle(plist)
        num_mafia = max(1, len(plist) // 4)
        self.mafia = set(plist[:num_mafia])
        for pid in plist:
            self.roles[pid] = "مافيا" if pid in self.mafia else "مدني"
        self.alive = set(plist)
    
    def check(self, txt):
        return False
