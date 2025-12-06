import random
from linebot.models import TextSendMessage, FlexSendMessage
from constants import *
import json

class GameManager:
    def __init__(self, db, ui, line_bot_api):
        self.db = db
        self.ui = ui
        self.line_bot_api = line_bot_api
        
        # بيانات الألعاب
        self.truth_questions = [
            "ما هو أكبر كذبة قلتها في حياتك؟",
            "من هو الشخص الذي تحبه سراً؟",
            "ما هو أكثر شيء تندم عليه؟",
            "هل سبق وغششت في امتحان؟",
            "ما هو أغرب حلم رأيته؟",
            "من هو الشخص الذي لا تطيقه ولكنك تتظاهر بعكس ذلك؟",
            "ما هو أكثر موقف محرج مررت به؟",
            "هل سبق وسرقت شيئاً؟",
            "ما هو أكبر سر تخفيه عن أصدقائك؟",
            "من هو آخر شخص بحثت عنه على وسائل التواصل؟"
        ]
        
        self.dare_challenges = [
            "ارسل رسالة لآخر شخص في جهات الاتصال تقول فيها: أنا أفكر فيك",
            "انشر صورة قديمة لك وأنت صغير",
            "اتصل بصديق واطلب منه مبلغ مالي",
            "ارقص أمام الكاميرا لمدة 30 ثانية",
            "اكتب منشور على حسابك يمدح فيه شخص عشوائي",
            "قلد صوت أحد المشاهير",
            "اعترف بشيء لم تخبر به أحد من قبل",
            "اتصل بأحد أقاربك وقل له أنك تحبه",
            "غير اسمك إلى اسم مضحك ليوم كامل",
            "ارسل صورة سيلفي بوجه مضحك"
        ]
        
        self.would_you_rather = [
            ("تفقد القدرة على الكلام", "تفقد القدرة على المشي"),
            ("تعيش في الماضي", "تعيش في المستقبل"),
            ("تكون غنياً وحيداً", "تكون فقيراً ومحاطاً بالأحباء"),
            ("تقرأ أفكار الناس", "تكون غير مرئي"),
            ("تعيش بدون موسيقى", "تعيش بدون أفلام"),
            ("تأكل نفس الوجبة كل يوم", "لا تأكل لحم أبداً"),
            ("تسافر للفضاء", "تستكشف أعماق البحار"),
            ("تعيش 200 سنة", "تعيش حياة قصيرة وسعيدة"),
            ("تكون ذكياً جداً", "تكون جميلاً جداً"),
            ("تفقد ذكرياتك", "تفقد قدرتك على تكوين ذكريات جديدة")
        ]
        
        self.trivia_questions = [
            {"q": "ما هي عاصمة فرنسا؟", "options": ["باريس", "لندن", "برلين", "مدريد"], "answer": 0},
            {"q": "كم عدد قارات العالم؟", "options": ["5", "6", "7", "8"], "answer": 2},
            {"q": "من هو مخترع المصباح الكهربائي؟", "options": ["نيوتن", "أديسون", "تسلا", "آينشتاين"], "answer": 1},
            {"q": "ما هو أكبر كوكب في المجموعة الشمسية؟", "options": ["الأرض", "المشتري", "زحل", "المريخ"], "answer": 1},
            {"q": "كم عدد أيام السنة الميلادية؟", "options": ["364", "365", "366", "360"], "answer": 1},
            {"q": "ما هي أكبر دولة في العالم من حيث المساحة؟", "options": ["الصين", "كندا", "روسيا", "أمريكا"], "answer": 2},
            {"q": "من هو أسرع حيوان في العالم؟", "options": ["الفهد", "النمر", "الأسد", "الذئب"], "answer": 0},
            {"q": "كم عدد ألوان قوس قزح؟", "options": ["5", "6", "7", "8"], "answer": 2},
            {"q": "ما هو أطول نهر في العالم؟", "options": ["النيل", "الأمازون", "الفرات", "دجلة"], "answer": 0},
            {"q": "كم عدد أسنان الإنسان البالغ؟", "options": ["28", "30", "32", "34"], "answer": 2}
        ]
        
        self.words = [
            "مدرسة", "كتاب", "قلم", "شجرة", "سيارة", "بيت", "باب", "نافذة",
            "طائرة", "سفينة", "جبل", "بحر", "نهر", "غابة", "صحراء", "مدينة",
            "قرية", "مطعم", "مستشفى", "جامعة", "مكتبة", "حديقة", "متحف", "مسجد"
        ]
        
        self.cities = {
            "أ": ["أبها", "أبوظبي"],
            "ب": ["بغداد", "بيروت", "برلين"],
            "ت": ["تونس", "طهران", "تبوك"],
            "ج": ["جدة", "جنيف"],
            "د": ["دمشق", "دبي", "دلهي"],
            "ر": ["الرياض", "روما", "رابغ"],
            "ع": ["عمان", "عدن"],
            "ق": ["القاهرة", "قطر", "القصيم"],
            "م": ["مكة", "المدينة", "مسقط", "مراكش"],
            "ن": ["نيويورك", "نجران"]
        }
        
        self.countries = {
            "أ": ["الأردن", "الإمارات", "أفغانستان"],
            "ب": ["البحرين", "باكستان", "بنغلاديش"],
            "ت": ["تركيا", "تونس", "تايلاند"],
            "ج": ["الجزائر", "جيبوتي"],
            "س": ["السعودية", "سوريا", "السودان", "سلطنة عمان"],
            "ع": ["العراق", "عمان"],
            "ف": ["فلسطين", "فرنسا", "فنلندا"],
            "ق": ["قطر", "الكويت"],
            "ل": ["لبنان", "ليبيا"],
            "م": ["مصر", "المغرب", "ماليزيا", "موريتانيا"],
            "ي": ["اليمن", "اليابان"]
        }
        
        self.animals = {
            "أ": ["أسد", "أرنب", "أفعى"],
            "ب": ["بقرة", "ببغاء", "بطة"],
            "ت": ["تمساح", "ثعلب", "ثور"],
            "ج": ["جمل", "جاموس"],
            "ح": ["حمار", "حصان", "حوت"],
            "خ": ["خروف", "خنزير"],
            "د": ["دب", "ديك", "دجاجة"],
            "ذ": ["ذئب", "ذبابة"],
            "ز": ["زرافة", "زواحف"],
            "س": ["سمكة", "سلحفاة", "سنجاب"],
            "ف": ["فيل", "فهد", "فراشة"],
            "ق": ["قط", "قرد", "قنفذ"],
            "ك": ["كلب", "كنغر"],
            "ن": ["نمر", "نحلة", "نسر"]
        }
    
    def handle_game_command(self, event, text, user_id, group_id):
        """معالجة أوامر الألعاب"""
        complex_games = ['احزر', 'لوريت', 'مافيا']
        if any(cmd in text for cmd in complex_games):
            if self.db.has_active_game(group_id):
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=SYSTEM_MESSAGES['game_active'])
                )
                return
        
        if text in ['صراحة', '/truth']:
            self.play_truth(event, user_id)
        elif text in ['جرأة', '/dare']:
            self.play_dare(event, user_id)
        elif text in ['لو خيروك', '/wouldyourather']:
            self.play_would_you_rather(event, user_id, group_id)
        elif text in ['سؤال', '/question']:
            self.play_trivia(event, user_id, group_id)
        elif text in ['رياضيات', '/math']:
            self.play_math(event, user_id, group_id)
        elif text in ['احزر', '/guess']:
            self.start_guess_game(event, user_id, group_id)
        elif text in ['كلمة', '/word']:
            self.play_word(event, user_id, group_id)
        elif text in ['عكس', '/reverse']:
            self.play_reverse(event, user_id, group_id)
        elif text in ['مدن', '/cities']:
            self.play_category(event, user_id, group_id, 'cities')
        elif text in ['دول', '/countries']:
            self.play_category(event, user_id, group_id, 'countries')
        elif text in ['حيوانات', '/animals']:
            self.play_category(event, user_id, group_id, 'animals')
        elif text in ['لوريت', '/lariat']:
            self.start_lariat_game(event, user_id, group_id)
        elif text in ['مافيا', '/mafia']:
            self.start_mafia_game(event, user_id, group_id)
        else:
            self.check_active_game_answer(event, text, user_id, group_id)
    
    def play_truth(self, event, user_id):
        question = random.choice(self.truth_questions)
        try:
            profile = self.line_bot_api.get_profile(user_id)
            name = profile.display_name
        except:
            name = "اللاعب"
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{name}\n\n{question}")
        )
        self.db.record_game_stat(user_id, 'truth', 'played', 5)
        self.db.update_user_stats(user_id, points=5)
    
    def play_dare(self, event, user_id):
        challenge = random.choice(self.dare_challenges)
        try:
            profile = self.line_bot_api.get_profile(user_id)
            name = profile.display_name
        except:
            name = "اللاعب"
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{name}\n\nتحدي: {challenge}")
        )
        self.db.record_game_stat(user_id, 'dare', 'played', 5)
        self.db.update_user_stats(user_id, points=5)
    
    def play_would_you_rather(self, event, user_id, group_id):
        options = random.choice(self.would_you_rather)
        theme = self.db.get_user_theme(user_id)
        flex = self.ui.create_would_you_rather_flex(options[0], options[1], theme)
        
        self.db.create_active_game(group_id, 'wouldyourather', {
            'options': options,
            'votes': {}
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text='لو خيروك', contents=flex)
        )
    
    def play_trivia(self, event, user_id, group_id):
        question_data = random.choice(self.trivia_questions)
        theme = self.db.get_user_theme(user_id)
        flex = self.ui.create_game_question_flex(
            question_data['q'],
            question_data['options'],
            theme
        )
        
        self.db.create_active_game(group_id, 'trivia', {
            'question': question_data,
            'answered': False
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text='سؤال', contents=flex)
        )
    
    def play_math(self, event, user_id, group_id):
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            answer = num1 + num2
            question = f"{num1} + {num2} = ؟"
        elif operation == '-':
            answer = num1 - num2
            question = f"{num1} - {num2} = ؟"
        else:
            answer = num1 * num2
            question = f"{num1} × {num2} = ؟"
        
        self.db.create_active_game(group_id, 'math', {
            'question': question,
            'answer': answer,
            'answered': False
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"احسب:\n\n{question}")
        )
    
    def start_guess_game(self, event, user_id, group_id):
        number = random.randint(1, 100)
        
        self.db.create_active_game(group_id, 'guess', {
            'number': number,
            'attempts': 0,
            'max_attempts': 7
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="لعبة احزر الرقم\n\nفكرت في رقم بين 1 و 100\nحاول تخمينه في 7 محاولات")
        )
    
    def play_word(self, event, user_id, group_id):
        word = random.choice(self.words)
        shuffled = ''.join(random.sample(word, len(word)))
        
        while shuffled == word:
            shuffled = ''.join(random.sample(word, len(word)))
        
        self.db.create_active_game(group_id, 'word', {
            'word': word,
            'shuffled': shuffled,
            'answered': False
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"رتب الحروف لتكوين كلمة صحيحة:\n\n{shuffled}")
        )
    
    def play_reverse(self, event, user_id, group_id):
        word = random.choice(self.words)
        reversed_word = word[::-1]
        
        self.db.create_active_game(group_id, 'reverse', {
            'word': word,
            'answered': False
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"ما هي الكلمة؟\n\n{reversed_word}")
        )
    
    def play_category(self, event, user_id, group_id, category):
        if category == 'cities':
            data = self.cities
            name = "مدينة"
        elif category == 'countries':
            data = self.countries
            name = "دولة"
        else:
            data = self.animals
            name = "حيوان"
        
        letter = random.choice(list(data.keys()))
        
        self.db.create_active_game(group_id, category, {
            'letter': letter,
            'valid_answers': data[letter],
            'answered': False
        })
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"اذكر {name} يبدأ بحرف:\n\n{letter}")
        )
    
    def start_lariat_game(self, event, user_id, group_id):
        try:
            profile = self.line_bot_api.get_profile(user_id)
            name = profile.display_name
        except:
            name = "اللاعب"
        
        existing = self.db.get_lariat_game(group_id)
        if existing:
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="يوجد لعبة لوريت نشطة بالفعل")
            )
            return
        
        first_word = random.choice(self.words)
        self.db.create_lariat_game(group_id, first_word, [user_id])
        
        last_letter = first_word[-1]
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"بدأت لعبة لوريت\n\n{name} بدأ بكلمة: {first_word}\n\nالدور التالي: اكتب كلمة تبدأ بحرف {last_letter}"
            )
        )
    
    def start_mafia_game(self, event, user_id, group_id):
        try:
            profile = self.line_bot_api.get_profile(user_id)
            name = profile.display_name
        except:
            name = "اللاعب"
        
        existing = self.db.get_mafia_game(group_id)
        if existing:
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="يوجد لعبة مافيا نشطة بالفعل")
            )
            return
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"لعبة المافيا\n\nيحتاج من 5 إلى 10 لاعبين\n\n{name} انضم للعبة\n\nأرسل 'انضم' للمشاركة\nأرسل 'ابدأ' لبدء اللعبة"
            )
        )
        
        self.db.create_active_game(group_id, 'mafia_lobby', {
            'players': [user_id],
            'ready': False
        })
    
    def leave_game(self, user_id, group_id):
        try:
            profile = self.line_bot_api.get_profile(user_id)
            name = profile.display_name
        except:
            name = "اللاعب"
        
        lariat = self.db.get_lariat_game(group_id)
        if lariat and user_id in lariat['players']:
            players = lariat['players']
            players.remove(user_id)
            
            if len(players) < 2:
                self.db.delete_lariat_game(group_id)
                return f"{name} انسحب\nانتهت اللعبة - لا يوجد لاعبين كافيين"
            
            return f"{name} انسحب من اللعبة"
        
        return "أنت لست في لعبة نشطة"
    
    def handle_postback(self, event, data, user_id, source_id, is_group):
        if data == 'data=stats':
            stats = self.db.get_user_stats(user_id)
            theme = self.db.get_user_theme(user_id)
            stats_flex = self.ui.create_stats_card(stats, theme)
            
            self.line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text='احصائياتك', contents=stats_flex)
            )
        
        elif data == 'data=themes':
            current_theme = self.db.get_user_theme(user_id)
            themes_flex = self.ui.create_themes_menu(current_theme)
            
            self.line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text='الثيمات', contents=themes_flex)
            )
        
        elif data.startswith('answer='):
            if not is_group:
                return
            
            answer_idx = int(data.split('=')[1])
            game_data = self.db.get_active_game(source_id, 'trivia')
            
            if game_data and not game_data['answered']:
                correct = answer_idx == game_data['question']['answer']
                
                try:
                    profile = self.line_bot_api.get_profile(user_id)
                    name = profile.display_name
                except:
                    name = "اللاعب"
                
                if correct:
                    points = GAME_SETTINGS['points_correct']
                    self.db.update_user_stats(user_id, won=True, points=points)
                    self.db.record_game_stat(user_id, 'trivia', 'win', points)
                    message = f"إجابة صحيحة {name}\n+{points} نقطة"
                else:
                    points = GAME_SETTINGS['points_wrong']
                    self.db.update_user_stats(user_id, points=points)
                    self.db.record_game_stat(user_id, 'trivia', 'lose', points)
                    correct_answer = game_data['question']['options'][game_data['question']['answer']]
                    message = f"إجابة خاطئة {name}\nالإجابة الصحيحة: {correct_answer}"
                
                game_data['answered'] = True
                self.db.update_active_game(source_id, 'trivia', game_data)
                
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=message)
                )
        
        elif data.startswith('choice='):
            if not is_group:
                return
            
            choice = data.split('=')[1]
            game_data = self.db.get_active_game(source_id, 'wouldyourather')
            
            if game_data:
                try:
                    profile = self.line_bot_api.get_profile(user_id)
                    name = profile.display_name
                except:
                    name = "اللاعب"
                
                chosen_option = game_data['options'][0] if choice == '1' else game_data['options'][1]
                
                self.db.record_game_stat(user_id, 'wouldyourather', 'played', 5)
                self.db.update_user_stats(user_id, points=5)
                
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{name} اختار:\n{chosen_option}")
                )
    
    def check_active_game_answer(self, event, text, user_id, group_id):
        try:
            profile = self.line_bot_api.get_profile(user_id)
            name = profile.display_name
        except:
            name = "اللاعب"
        
        # لعبة رياضيات
        math_game = self.db.get_active_game(group_id, 'math')
        if math_game and not math_game['answered']:
            try:
                answer = int(text)
                if answer == math_game['answer']:
                    points = GAME_SETTINGS['points_correct']
                    self.db.update_user_stats(user_id, won=True, points=points)
                    self.db.record_game_stat(user_id, 'math', 'win', points)
                    
                    math_game['answered'] = True
                    self.db.update_active_game(group_id, 'math', math_game)
                    
                    self.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"إجابة صحيحة {name}\n+{points} نقطة")
                    )
                    return
            except:
                pass
        
        # لعبة احزر
        guess_game = self.db.get_active_game(group_id, 'guess')
        if guess_game:
            try:
                guess = int(text)
                guess_game['attempts'] += 1
                
                if guess == guess_game['number']:
                    points = GAME_SETTINGS['points_win']
                    self.db.update_user_stats(user_id, won=True, points=points)
                    self.db.record_game_stat(user_id, 'guess', 'win', points)
                    self.db.delete_active_game(group_id, 'guess')
                    
                    self.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"مبروك {name}\nالرقم صحيح: {guess}\n+{points} نقطة")
                    )
                    return
                
                elif guess_game['attempts'] >= guess_game['max_attempts']:
                    self.db.delete_active_game(group_id, 'guess')
                    self.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"انتهت المحاولات\nالرقم الصحيح كان: {guess_game['number']}")
                    )
                    return
                
                else:
                    hint = "أكبر" if guess < guess_game['number'] else "أصغر"
                    remaining = guess_game['max_attempts'] - guess_game['attempts']
                    
                    self.db.update_active_game(group_id, 'guess', guess_game)
                    
                    self.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"الرقم {hint}\nالمحاولات المتبقية: {remaining}")
                    )
                    return
            except:
                pass
        
        # لعبة كلمة
        word_game = self.db.get_active_game(group_id, 'word')
        if word_game and not word_game['answered']:
            if text.strip() == word_game['word']:
                points = GAME_SETTINGS['points_correct']
                self.db.update_user_stats(user_id, won=True, points=points)
                self.db.record_game_stat(user_id, 'word', 'win', points)
                
                word_game['answered'] = True
                self.db.update_active_game(group_id, 'word', word_game)
                
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"إجابة صحيحة {name}\nالكلمة: {word_game['word']}\n+{points} نقطة")
                )
                return
        
        # لعبة عكس
        reverse_game = self.db.get_active_game(group_id, 'reverse')
        if reverse_game and not reverse_game['answered']:
            if text.strip() == reverse_game['word']:
                points = GAME_SETTINGS['points_correct']
                self.db.update_user_stats(user_id, won=True, points=points)
                self.db.record_game_stat(user_id, 'reverse', 'win', points)
                
                reverse_game['answered'] = True
                self.db.update_active_game(group_id, 'reverse', reverse_game)
                
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"إجابة صحيحة {name}\nالكلمة: {reverse_game['word']}\n+{points} نقطة")
                )
                return
        
        # ألعاب الفئات
        for category in ['cities', 'countries', 'animals']:
            cat_game = self.db.get_active_game(group_id, category)
            if cat_game and not cat_game['answered']:
                if text.strip() in cat_game['valid_answers']:
                    points = GAME_SETTINGS['points_correct']
                    self.db.update_user_stats(user_id, won=True, points=points)
                    self.db.record_game_stat(user_id, category, 'win', points)
                    
                    cat_game['answered'] = True
                    self.db.update_active_game(group_id, category, cat_game)
                    
                    self.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"إجابة صحيحة {name}\n{text}\n+{points} نقطة")
                    )
                    return
        
        # لعبة لوريت
        lariat = self.db.get_lariat_game(group_id)
        if lariat:
            last_letter = lariat['current_word'][-1]
            word = text.strip()
            
            if word[0] == last_letter and word not in lariat['used_words'] and len(word) > 1:
                players = lariat['players']
                current_idx = players.index(lariat['current_player'])
                next_idx = (current_idx + 1) % len(players)
                next_player = players[next_idx]
                
                self.db.update_lariat_game(group_id, word, next_player)
                
                points = 5
                self.db.update_user_stats(user_id, points=points)
                self.db.record_game_stat(user_id, 'lariat', 'played', points)
                
                new_last_letter = word[-1]
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{name}: {word}\n\nالدور التالي: كلمة تبدأ بحرف {new_last_letter}")
                )
                return
        
        # لعبة المافيا - انضمام
        mafia_lobby = self.db.get_active_game(group_id, 'mafia_lobby')
        if mafia_lobby and text == 'انضم':
            if user_id not in mafia_lobby['players']:
                mafia_lobby['players'].append(user_id)
                self.db.update_active_game(group_id, 'mafia_lobby', mafia_lobby)
                
                count = len(mafia_lobby['players'])
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{name} انضم للعبة\nعدد اللاعبين: {count}")
                )
                return
        
        # بدء لعبة المافيا
        if mafia_lobby and text == 'ابدأ':
            players_count = len(mafia_lobby['players'])
            
            if players_count < GAME_SETTINGS['min_players_mafia']:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"يحتاج 5 لاعبين على الأقل")
                )
                return
            
            players = mafia_lobby['players']
            roles = self.assign_mafia_roles(players)
            
            self.db.delete_active_game(group_id, 'mafia_lobby')
            self.db.create_mafia_game(group_id, players, roles)
            
            for player_id, role in roles.items():
                try:
                    role_text = self.get_role_description(role)
                    self.line_bot_api.push_message(
                        player_id,
                        TextSendMessage(text=f"دورك في اللعبة:\n{role_text}")
                    )
                except:
                    pass
            
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="بدأت لعبة المافيا\nتم إرسال الأدوار للاعبين في الخاص\n\nالليلة الأولى")
            )
    
    def assign_mafia_roles(self, players):
        roles = {}
        player_list = players.copy()
        random.shuffle(player_list)
        
        count = len(players)
        mafia_count = max(1, count // 3)
        
        for i in range(mafia_count):
            roles[player_list[i]] = 'mafia'
        
        if count >= 7:
            roles[player_list[mafia_count]] = 'doctor'
            roles[player_list[mafia_count + 1]] = 'detective'
            start_citizens = mafia_count + 2
        elif count >= 5:
            roles[player_list[mafia_count]] = 'doctor'
            start_citizens = mafia_count + 1
        else:
            start_citizens = mafia_count
        
        for i in range(start_citizens, count):
            roles[player_list[i]] = 'citizen'
        
        return roles
    
    def get_role_description(self, role):
        descriptions = {
            'mafia': 'أنت من المافيا\nهدفك: القضاء على جميع المواطنين',
            'doctor': 'أنت الطبيب\nيمكنك إنقاذ شخص كل ليلة',
            'detective': 'أنت المحقق\nيمكنك الكشف عن دور شخص كل ليلة',
            'citizen': 'أنت مواطن\nحاول اكتشاف المافيا'
        }
        return descriptions.get(role, ''
