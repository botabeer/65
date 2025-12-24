from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re

class BaseGame:
    def __init__(self, line_bot_api, questions_count=5):
        self.line_bot_api = line_bot_api
        self.questions_count = questions_count
        self.current_question = 0
        self.game_active = False
        self.game_name = "لعبة"
        self.scores = {}
        self.answered_users = set()
        self.supports_hint = True
        self.supports_reveal = True
        self.current_answer = None
        self.previous_question = None
        self.previous_answer = None

    def normalize_text(self, text):
        if not text:
            return ""
        text = text.strip().lower()
        trans = str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ؤ':'و','ئ':'ي','ء':'','ة':'ه','ى':'ي'})
        text = text.translate(trans)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def get_theme_colors(self, theme="light"):
        themes = {
            "light": {"primary":"#2563EB","success":"#10B981","warning":"#F59E0B",
                     "error":"#EF4444","info":"#3B82F6","text":"#1F2937","text2":"#6B7280",
                     "text3":"#9CA3AF","bg":"#FFFFFF","card":"#F9FAFB","border":"#E5E7EB",
                     "info_bg":"#DBEAFE"},
            "dark": {"primary":"#3B82F6","success":"#34D399","warning":"#FBBF24",
                    "error":"#F87171","info":"#60A5FA","text":"#F9FAFB","text2":"#D1D5DB",
                    "text3":"#9CA3AF","bg":"#1F2937","card":"#374151","border":"#4B5563",
                    "info_bg":"#1E3A8A"}
        }
        return themes.get(theme, themes["light"])

    def add_score(self, user_id, display_name, points):
        self.scores.setdefault(user_id, {'name': display_name, 'score': 0})
        self.scores[user_id]['score'] += points
        self.answered_users.add(user_id)
        return points

    def build_text_message(self, text):
        return TextMessage(text=text)

    def build_question_message(self, question_text, subtitle=None):
        c = self.get_theme_colors()
        contents = [
            {"type":"text","text":self.game_name,"size":"xl","weight":"bold","color":c["primary"],"align":"center"},
            {"type":"separator","margin":"md","color":c["border"]},
            {"type":"box","layout":"baseline","contents":[
                {"type":"text","text":f"{self.current_question + 1}","size":"sm","color":c["text2"],"flex":0},
                {"type":"text","text":f"من {self.questions_count}","size":"sm","color":c["text2"],"align":"end","flex":1}
            ],"margin":"md"},
            {"type":"separator","margin":"md","color":c["border"]},
            {"type":"text","text":question_text,"size":"md","color":c["text"],"wrap":True,"margin":"lg","align":"center"}
        ]
        
        if subtitle:
            contents.append({"type":"text","text":subtitle,"size":"xs","color":c["text3"],"wrap":True,"margin":"sm","align":"center"})
        
        contents.append({"type":"separator","margin":"lg","color":c["border"]})
        
        buttons = []
        if self.supports_hint:
            buttons.append({"type":"button","action":{"type":"message","label":"تلميح","text":"لمح"},"style":"secondary","height":"sm"})
        if self.supports_reveal:
            buttons.append({"type":"button","action":{"type":"message","label":"الاجابة","text":"جاوب"},"style":"secondary","height":"sm","color":c["warning"]})
        buttons.append({"type":"button","action":{"type":"message","label":"انسحب","text":"انسحب"},"style":"secondary","height":"sm","color":c["error"]})
        
        if buttons:
            contents.append({"type":"box","layout":"horizontal","contents":buttons,"spacing":"sm","margin":"md"})
        
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":contents,
            "backgroundColor":c["bg"],"paddingAll":"20px"}
        }))

    def _create_flex_with_buttons(self, alt_text, bubble):
        return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(bubble))

    def _create_text_message(self, text):
        return TextMessage(text=text)

    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        return self.get_question()

    def get_question(self):
        return self.build_text_message("لم يتم تنفيذ السؤال")

    def check_answer(self, user_answer, user_id, display_name):
        return None

    def end_game(self):
        self.game_active = False
        if not self.scores:
            return {"game_over":True,"points":0,"message":"انتهت اللعبة"}
        
        sorted_players = sorted(self.scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        c = self.get_theme_colors()
        contents = [
            {"type":"text","text":f"نتائج {self.game_name}","weight":"bold","size":"xl","color":c["primary"],"align":"center"},
            {"type":"separator","margin":"lg","color":c["border"]},
            {"type":"text","text":f"الفائز: {winner['name']}","size":"lg","weight":"bold","color":c["success"],"align":"center","margin":"lg"},
            {"type":"text","text":f"النقاط: {winner['score']}","size":"md","color":c["text"],"align":"center","margin":"sm"},
            {"type":"separator","margin":"lg","color":c["border"]}
        ]
        
        if len(sorted_players) > 1:
            contents.append({"type":"text","text":"الترتيب","size":"sm","weight":"bold","color":c["text2"],"align":"center","margin":"md"})
            for i, (uid, p) in enumerate(sorted_players[:5], 1):
                contents.append({"type":"text","text":f"{i}. {p['name']} - {p['score']}","size":"xs","color":c["text"],"margin":"xs"})
        
        contents.append({"type":"separator","margin":"lg","color":c["border"]})
        contents.append({"type":"box","layout":"horizontal","contents":[
            {"type":"button","action":{"type":"message","label":"اعادة","text":self.game_name},"style":"primary","color":c["primary"],"height":"sm"},
            {"type":"button","action":{"type":"message","label":"البداية","text":"بداية"},"style":"secondary","height":"sm"}
        ],"spacing":"sm","margin":"md"})
        
        flex_msg = FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":contents,
            "backgroundColor":c["bg"],"paddingAll":"20px"}
        }))
        
        return {"game_over":True,"points":winner['score'],"won":True,"response":flex_msg,"message":f"فاز {winner['name']}"}
