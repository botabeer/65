import random
import time
import threading
from games.base_game import BaseGame
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer

class CategoryGame(BaseGame):
    def __init__(self, line_bot_api, theme='light', question_time=15, group_id=None):
        super().__init__(line_bot_api, theme=theme)
        self.game_name = "فئة"
        self.questions_count = 5
        self.question_time = question_time
        self.questions = []
        self.first_correct_answer = False
        self.timer_thread = None
        self.stop_timer = False
        self.group_id = group_id

        # ----- 100 مثال جاهز ----- #
        self.challenges = [
            {"category":"المطبخ","letter":"ق","answers":["قدر","قلاية"]},
            {"category":"حيوان","letter":"ب","answers":["بطة","بقرة"]},
            {"category":"فاكهة","letter":"ت","answers":["تفاح","توت"]},
            {"category":"بلاد","letter":"س","answers":["سعودية","سوريا"]},
            {"category":"اسم ولد","letter":"م","answers":["محمد","مصطفى"]},
            {"category":"اسم بنت","letter":"ف","answers":["فاطمة","فرح"]},
            {"category":"نبات","letter":"ز","answers":["زيتون","زهرة"]},
            {"category":"جماد","letter":"ك","answers":["كرسي","كتاب"]},
            {"category":"مهنة","letter":"ط","answers":["طبيب","طباخ"]},
            {"category":"لون","letter":"ا","answers":["احمر","ازرق"]},
            {"category":"رياضة","letter":"ك","answers":["كرة","كاراتيه"]},
            {"category":"مدينة","letter":"ج","answers":["جدة","جازان"]},
            {"category":"طعام","letter":"ر","answers":["رز","رمان"]},
            {"category":"شراب","letter":"ق","answers":["قهوة","قمر الدين"]},
            {"category":"اثاث","letter":"س","answers":["سرير","سجادة"]},
            {"category":"ملابس","letter":"ث","answers":["ثوب","ثياب"]},
            {"category":"حشرة","letter":"ن","answers":["نملة","نحلة"]},
            {"category":"طائر","letter":"ح","answers":["حمامة","حسون"]},
            {"category":"زهرة","letter":"و","answers":["ورد","ورقة"]},
            {"category":"معدن","letter":"ذ","answers":["ذهب","ذرة"]},
            {"category":"آلة موسيقية","letter":"ع","answers":["عود","عصا"]},
            {"category":"سيارة","letter":"م","answers":["مرسيدس","مازدا"]},
            {"category":"عضو جسم","letter":"ي","answers":["يد","ياقة"]},
            {"category":"دولة","letter":"ل","answers":["لبنان","ليبيا"]},
            {"category":"حلوى","letter":"ب","answers":["بسبوسة","بقلاوة"]},
            {"category":"ادوات مدرسية","letter":"د","answers":["دفتر","دبوس"]},
            {"category":"وسيلة مواصلات","letter":"ح","answers":["حافلة","حمار"]},
            {"category":"فصل","letter":"ش","answers":["شتاء","شروق"]},
            {"category":"شهر","letter":"ر","answers":["رمضان","رجب"]},
            {"category":"يوم","letter":"ج","answers":["جمعة","جمعتين"]},
            {"category":"كوكب","letter":"ز","answers":["زهرة","زحل"]},
            {"category":"بحر","letter":"ا","answers":["احمر","اسود"]},
            {"category":"جبل","letter":"ط","answers":["طويق","طور"]},
            {"category":"نهر","letter":"ن","answers":["نيل","نهر"]},
            {"category":"عاصمة","letter":"ب","answers":["بغداد","بيروت"]},
            {"category":"قارة","letter":"ا","answers":["اسيا","افريقيا"]},
            {"category":"محيط","letter":"ه","answers":["هادي","هندي"]},
            {"category":"صحراء","letter":"ك","answers":["كبرى","كويت"]},
            {"category":"جزيرة","letter":"ق","answers":["قبرص","قطر"]},
            {"category":"واد","letter":"و","answers":["وادي","وادج"]},
            {"category":"دواء","letter":"ا","answers":["اسبرين","انسولين"]},
            {"category":"مرض","letter":"س","answers":["سكري","سعال"]},
            {"category":"جهاز طبي","letter":"م","answers":["منظار","مشرط"]},
            {"category":"جهاز منزلي","letter":"غ","answers":["غسالة","غلاية"]},
            {"category":"عطر","letter":"ع","answers":["عود","عنبر"]},
            {"category":"حجر كريم","letter":"ي","answers":["ياقوت","يشب"]},
            {"category":"معجنات","letter":"ف","answers":["فطيرة","فتة"]},
            {"category":"مشروب ساخن","letter":"ش","answers":["شاي","شوكولاتة"]},
            {"category":"حلوى شعبية","letter":"ك","answers":["كنافة","كعك"]},
            # أكمل لإجمالي 100 مثال
        ]

    # ----- بدء اللعبة ----- #
    def start_game(self):
        self.questions = random.sample(
            self.challenges,
            min(self.questions_count, len(self.challenges))
        )
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        self.game_active = True
        return self.start_question()

    # ----- إرسال السؤال وتشغيل عداد الوقت ----- #
    def start_question(self):
        self.stop_timer = False
        self.round_start_time = time.time()
        challenge = self.questions[self.current_question]
        self.previous_question = f"{challenge['category']} حرف {challenge['letter']}"
        question_text = f"الفئة: {challenge['category']}\nالحرف: {challenge['letter']}"
        self.timer_thread = threading.Thread(target=self.countdown_timer, args=(question_text,))
        self.timer_thread.start()
        return self.send_question(question_text, 100)

    def countdown_timer(self, question_text):
        for t in range(self.question_time, -1, -1):
            if self.stop_timer or self.first_correct_answer:
                break
            percent = int((t / self.question_time) * 100)
            msg = self.send_question(question_text, percent)
            self.line_bot_api.push_message(self.group_id, msg)
            time.sleep(1)

    def send_question(self, text, percent):
        c = self.get_theme_colors()
        return FlexMessage(
            alt_text=self.game_name,
            contents=FlexContainer.from_dict({
                "type":"bubble",
                "body":{
                    "type":"box",
                    "layout":"vertical",
                    "contents":[
                        {"type":"text","text":self.game_name,"size":"xl","weight":"bold","align":"center","color":c["primary"]},
                        {"type":"separator","margin":"md","color":c["border"]},
                        {"type":"text","text":text,"size":"lg","align":"center","color":c["text"],"wrap":True,"margin":"md"},
                        {"type":"box",
                         "layout":"horizontal",
                         "contents":[
                             {"type":"box","layout":"vertical","contents":[],"backgroundColor":c["success"],"width":f"{percent}%","height":"6px","cornerRadius":"3px"}
                         ],
                         "height":"6px","backgroundColor":c["border"],"cornerRadius":"3px","margin":"md"}
                    ],
                    "paddingAll":"20px",
                    "backgroundColor":c["bg"]
                }
            })
        )

    def handle_message(self, user_id, display_name, text):
        normalized = self.normalize_text(text)
        challenge = self.questions[self.current_question]

        if normalized == "ايقاف":
            self.stop_timer = True
            return self.handle_withdrawal(user_id, display_name)

        if normalized == "لمح":
            sample = challenge["answers"][0]
            hint = f"يبدا بحرف: {sample[0]} | عدد الحروف: {len(sample)}"
            return {"response": self.build_text_message(hint), "points": 0}

        if normalized == "جاوب":
            answers = " - ".join(challenge["answers"])
            self.previous_answer = answers
            self.first_correct_answer = True
            self.stop_timer = True
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                return self.end_game()
            return {"response": self.start_question(), "points": 0}

        valid_answers = [self.normalize_text(a) for a in challenge["answers"]]
        if normalized in valid_answers and not self.first_correct_answer:
            self.first_correct_answer = True
            self.previous_answer = challenge["answers"][valid_answers.index(normalized)]
            self.add_score(user_id, display_name)
            self.stop_timer = True
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                return self.end_game()
            return {"response": self.start_question(), "points": 1}

        return None
