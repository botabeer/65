from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import time, re

class SmartBaseGame:
    THEMES = {
        "فاتح": {"primary":"#2563EB","success":"#10B981","warning":"#F59E0B","error":"#EF4444","text":"#1F2937","text2":"#6B7280","border":"#E5E7EB","bg":"#F9FAFB","card":"#FFFFFF"},
        "داكن": {"primary":"#3B82F6","success":"#34D399","warning":"#FBBF24","error":"#F87171","text":"#F9FAFB","text2":"#D1D5DB","border":"#4B5563","bg":"#1F2937","card":"#374151"}
    }

    def __init__(self, line_bot_api=None, questions_count=5, game_type="competitive", theme="فاتح", level=1):
        self.line_bot_api = line_bot_api
        self.questions_count = questions_count
        self.current_question = 0
        self.game_active = False
        self.game_name = "لعبة"
        self.scores = {}
        self.answered_users = set()
        self.current_answer = None
        self.prev_answer = None
        self.start_time = None
        self.game_type = game_type
        self.theme_name = theme
        self.theme = self.THEMES.get(theme, self.THEMES["فاتح"])
        self.level = level
        self.supports_hint = game_type in ["competitive","fast"]
        self.supports_reveal = game_type=="competitive"

    def normalize_text(self, text):
        if not text: return ""
        text = text.strip().lower()
        trans = str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ؤ':'و','ئ':'ي','ء':'','ة':'ه','ى':'ي'})
        text = text.translate(trans)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def add_score(self, user_id, display_name, points=1):
        self.scores.setdefault(user_id, {'name': display_name, 'score':0})
        self.scores[user_id]['score'] += points
        self.answered_users.add(user_id)
        return points

    # ======== نافذة السؤال أثناء اللعب ========
    def build_question(self, question_text):
        c = self.theme
        contents = []

        # إجابة السؤال السابق
        if self.prev_answer and self.game_type!="entertainment":
            contents.append({"type":"text","text":f"إجابة السؤال السابق: {self.prev_answer}","size":"xs","color":c["text2"],"wrap":True,"align":"center","margin":"sm"})

        # عنوان اللعبة والمستوى
        contents.append({"type":"text","text":f"{self.game_name} (مستوى {self.level})","size":"lg","weight":"bold","align":"center","color":c["text"]})

        # Progress Bar
        if self.game_type!="entertainment":
            progress=int(((self.current_question+1)/self.questions_count)*100)
            contents.append({"type":"box","layout":"vertical","margin":"md","contents":[
                {"type":"box","layout":"horizontal","height":"8px","backgroundColor":c["border"],
                 "cornerRadius":"4px","contents":[{"type":"box","layout":"horizontal","width":f"{progress}%","backgroundColor":c["primary"],"cornerRadius":"4px","contents":[]}]},
                {"type":"text","text":f"{self.current_question+1}/{self.questions_count}","size":"xs","align":"center","margin":"sm","color":c["text2"]}
            ]})

        contents.append({"type":"separator","margin":"lg"})
        contents.append({"type":"text","text":question_text,"size":"md","wrap":True,"align":"center","margin":"lg","color":c["text"]})

        # أزرار ذكية
        buttons=[]
        if self.supports_hint:
            buttons.append({"type":"button","action":{"type":"message","label":"تلميح","text":"لمح"},"style":"secondary","height":"sm"})
        if self.supports_reveal:
            buttons.append({"type":"button","action":{"type":"message","label":"الاجابة","text":"جاوب"},"style":"primary","height":"sm","color":c["warning"]})
        buttons.append({"type":"button","action":{"type":"message","label":"ايقاف","text":"ايقاف"},"style":"secondary","height":"sm","color":c["error"]})
        if buttons:
            contents.append({"type":"box","layout":"horizontal","spacing":"sm","margin":"md","contents":buttons})

        self.start_time=time.time()
        bubble={"type":"bubble","body":{"type":"box","layout":"vertical","paddingAll":"20px","backgroundColor":c["bg"],"contents":contents}}
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))

    # ======== التحقق من الإجابة ========
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active: return None
        normalized = self.normalize_text(user_answer)
        if user_id not in self.scores:
            self.scores[user_id] = {"name":display_name,"score":0,"answered":False,"time":None}
        player = self.scores[user_id]
        if player.get("answered"): return None

        if normalized == self.normalize_text(self.current_answer):
            player["score"]+=1
            player["answered"]=True
            player["time"]=time.time()-self.start_time
            self.prev_answer=self.current_answer
            self.current_question+=1
            if self.current_question>=self.questions_count or self.game_type=="entertainment":
                return self.end_game()
            return self.build_question("السؤال التالي")
        return None

    # ======== نافذة إعلان الفائز ========
    def end_game(self):
        self.game_active=False
        c=self.theme
        sorted_players=sorted(self.scores.items(), key=lambda x:(-x[1]["score"], x[1].get("time",0)))
        winner = sorted_players[0][1] if sorted_players else {"name":"لاعب","score":0}
        result_text=f"انتهت اللعبة\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        if len(sorted_players)>1:
            result_text+="\n\nالترتيب:\n"
            for i,(uid,p) in enumerate(sorted_players,1):
                result_text+=f"{i}. {p['name']} - {p['score']}\n"

        bubble={"type":"bubble","body":{"type":"box","layout":"vertical","paddingAll":"20px","backgroundColor":c["bg"],"contents":[
            {"type":"text","text":"نتيجة اللعبة","size":"xl","weight":"bold","align":"center","color":c["text"]},
            {"type":"separator","margin":"lg"},
            {"type":"text","text":result_text,"size":"md","wrap":True,"color":c["text2"],"margin":"md"},
            {"type":"button","margin":"lg","height":"sm","style":"primary","color":c["primary"],"action":{"type":"message","label":"اعادة اللعب","text":"ابدأ"}},
            {"type":"button","margin":"md","height":"sm","style":"secondary","action":{"type":"message","label":"ايقاف","text":"ايقاف"}}
        ]}}
        return FlexMessage(alt_text="نتيجة اللعبة", contents=FlexContainer.from_dict(bubble))

    def start_game(self):
        self.game_active=True
        self.current_question=0
        self.scores={}
        self.answered_users=set()
        return self.build_question("السؤال الأول")
