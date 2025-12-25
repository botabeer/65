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
                     "error":"#EF4444","text":"#1F2937","text2":"#6B7280","border":"#E5E7EB",
                     "bg":"#F9FAFB","card":"#FFFFFF"},
            "dark": {"primary":"#3B82F6","success":"#34D399","warning":"#FBBF24",
                    "error":"#F87171","text":"#F9FAFB","text2":"#D1D5DB","border":"#4B5563",
                    "bg":"#1F2937","card":"#374151"}
        }
        return themes.get(theme, themes["light"])

    def add_score(self, user_id, display_name, points):
        self.scores.setdefault(user_id, {'name': display_name, 'score': 0})
        self.scores[user_id]['score'] += points
        self.answered_users.add(user_id)
        return points

    def build_text_message(self, text):
        return TextMessage(text=text)

    def build_question_message(self, question_text, subtitle=None, theme="light"):
        c = self.get_theme_colors(theme)
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
            contents.append({"type":"text","text":subtitle,"size":"xs","color":c["text2"],"wrap":True,"margin":"sm","align":"center"})
        
        contents.append({"type":"separator","margin":"lg","color":c["border"]})
        
        buttons = []
        if self.supports_hint:
            buttons.append({"type":"button","action":{"type":"message","label":"تلميح","text":"لمح"},"style":"secondary","height":"sm"})
        if self.supports_reveal:
            buttons.append({"type":"button","action":{"type":"message","label":"الاجابة","text":"جاوب"},"style":"secondary","height":"sm","color":c["warning"]})
        buttons.append({"type":"button","action":{"type":"message","label":"انسحب","text":"انسحب"},"style":"secondary","height":"sm","color":c["error"]})
        
        if buttons:
            contents.append({"type":"box","layout":"horizontal","contents":buttons,"spacing":"sm","margin":"md"})
        
        return FlexMessage(
            alt_text=self.game_name,
            contents=FlexContainer.from_dict({
                "type":"bubble",
                "body":{
                    "type":"box","layout":"vertical",
                    "contents":contents,
                    "paddingAll":"20px",
                    "backgroundColor":c["bg"]
                }
            })
        )

    def _create_flex_with_buttons(self, alt_text, bubble_dict):
        """Create flex message with buttons"""
        return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(bubble_dict))

    def _create_text_message(self, text):
        """Create text message"""
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
            return {"game_over":True,"points":0,"message":"انتهت اللعبة","response":self.build_text_message("انتهت اللعبة")}
        
        sorted_players = sorted(self.scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        result_text = f"انتهت اللعبة\n\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        
        if len(sorted_players) > 1:
            result_text += "\n\nالترتيب:\n"
            for i, (uid, p) in enumerate(sorted_players[:5], 1):
                result_text += f"{i}. {p['name']} - {p['score']}\n"
        
        return {
            "game_over":True,
            "points":winner['score'],
            "won":True,
            "response":self.build_text_message(result_text),
            "message":f"فاز {winner['name']}"
        }
