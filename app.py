from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_TOKEN or not LINE_SECRET:
    logger.error("Missing LINE credentials")
    sys.exit(1)

configuration = Configuration(access_token=LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

from database import DB
from ui import UI
from text_commands import TextCommands

DB.init()
TextCommands.load_all()

game_sessions = {}
waiting_for_name = set()
user_themes = {}
game_difficulties = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        user_id = event.source.user_id
        text = event.message.text.strip()
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        try:
            response = process(text, user_id, group_id, line_api)
            if response:
                msgs = response if isinstance(response, list) else [response]
                line_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=msgs))
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)

def process(text, user_id, group_id, line_api):
    t = text.lower().strip()
    user = DB.get_user(user_id)
    theme = user_themes.get(user_id, user['theme'] if user else 'light')
    
    if user_id in waiting_for_name:
        if 2 <= len(text) <= 50:
            DB.register_user(user_id, text.strip())
            waiting_for_name.discard(user_id)
            return TextMessage(text=f"تم التسجيل: {text}")
        waiting_for_name.discard(user_id)
        return None
    
    # أوامر نصية
    if t in ['سؤال', 'سوال']:
        return TextMessage(text=TextCommands.get_random('questions'))
    if t == 'تحدي':
        return TextMessage(text=TextCommands.get_random('challenges'))
    if t == 'اعتراف':
        return TextMessage(text=TextCommands.get_random('confessions'))
    if t == 'منشن':
        return TextMessage(text=TextCommands.get_random('mentions'))
    if t in ['حكمة', 'حكمه']:
        return TextMessage(text=TextCommands.get_random('quotes'))
    if t == 'موقف':
        return TextMessage(text=TextCommands.get_random('situations'))
    
    # القوائم الرئيسية
    if t in ['بداية', 'start', 'بدايه']:
        if user:
            DB.update_activity(user_id)
        return FlexMessage(alt_text="Bot 65", contents=FlexContainer.from_dict(
            UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme)))
    
    if t in ['مساعدة', 'help', 'مساعده']:
        return FlexMessage(alt_text="المساعدة", contents=FlexContainer.from_dict(UI.help_card(theme)))
    
    if t in ['العاب', 'ألعاب', 'الالعاب']:
        return FlexMessage(alt_text="الالعاب", contents=FlexContainer.from_dict(UI.games_menu(theme)))
    
    # التسجيل
    if t in ['تسجيل', 'تغيير']:
        waiting_for_name.add(user_id)
        return TextMessage(text="اكتب اسمك (2-50 حرف)")
    
    # الإحصائيات
    if t in ['نقاطي', 'احصائياتي']:
        if not user:
            return TextMessage(text="يجب التسجيل اولا")
        DB.update_activity(user_id)
        return FlexMessage(alt_text="احصائياتك", contents=FlexContainer.from_dict(UI.stats(user, theme)))
    
    if t in ['الصدارة', 'المتصدرين', 'الصداره']:
        leaders = DB.get_leaderboard()
        return FlexMessage(alt_text="الصدارة", contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme)))
    
    # تغيير الثيم
    if t == 'ثيم':
        if not user:
            return TextMessage(text="يجب التسجيل اولا")
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        user_themes[user_id] = new_theme
        return TextMessage(text=f"تم التغيير للثيم {'الداكن' if new_theme == 'dark' else 'الفاتح'}")
    
    # إيقاف اللعبة
    if t in ['ايقاف', 'stop', 'إيقاف']:
        if group_id in game_sessions:
            del game_sessions[group_id]
            if group_id in game_difficulties:
                del game_difficulties[group_id]
            return TextMessage(text="تم ايقاف اللعبة")
        return None
    
    # مستوى الصعوبة
    if t.startswith('صعوبة ') or t.startswith('مستوى '):
        try:
            level = int(t.split()[-1])
            if 1 <= level <= 5:
                game_difficulties[group_id] = level
                return TextMessage(text=f"تم تعيين الصعوبة: مستوى {level}")
        except:
            pass
        return TextMessage(text="استخدم: صعوبة 1 (الى 5)")
    
    if not user:
        return None
    
    # تشغيل الألعاب
    game_map = {
        'خمن': ('GuessGame', 'competitive'),
        'اسرع': ('FastGame', 'competitive'),
        'توافق': ('CompatibilityGame', 'entertainment'),
        'اغنيه': ('SongGame', 'competitive'),
        'ضد': ('OppositeGame', 'competitive'),
        'سلسله': ('ChainGame', 'competitive'),
        'تكوين': ('LettersGame', 'competitive'),
        'فئه': ('CategoryGame', 'competitive'),
        'لعبه': ('HumanAnimalGame', 'competitive'),
        'ذكاء': ('IqGame', 'competitive'),
        'ترتيب': ('ScrambleGame', 'competitive'),
        'لون': ('WordColorGame', 'competitive'),
        'روليت': ('RouletteGame', 'competitive'),
        'سين': ('SeenJeemGame', 'competitive'),
        'حروف': ('LetterGame', 'competitive'),
        'مافيا': ('MafiaGame', 'entertainment')
    }
    
    if t in game_map:
        try:
            from games import (
                GuessGame, FastGame, CompatibilityGame, SongGame,
                OppositeGame, ChainGame, LettersGame, CategoryGame,
                HumanAnimalGame, IqGame, ScrambleGame, WordColorGame,
                RouletteGame, SeenJeemGame, LetterGame, MafiaGame
            )
            
            game_classes = {
                'GuessGame': GuessGame, 'FastGame': FastGame,
                'CompatibilityGame': CompatibilityGame, 'SongGame': SongGame,
                'OppositeGame': OppositeGame, 'ChainGame': ChainGame,
                'LettersGame': LettersGame, 'CategoryGame': CategoryGame,
                'HumanAnimalGame': HumanAnimalGame, 'IqGame': IqGame,
                'ScrambleGame': ScrambleGame, 'WordColorGame': WordColorGame,
                'RouletteGame': RouletteGame, 'SeenJeemGame': SeenJeemGame,
                'LetterGame': LetterGame, 'MafiaGame': MafiaGame
            }
            
            game_class_name, game_type = game_map[t]
            game_class = game_classes.get(game_class_name)
            
            if game_class:
                difficulty = game_difficulties.get(group_id, 3)
                game = game_class(line_api, difficulty=difficulty, theme=theme)
                game_sessions[group_id] = game
                return game.start_game()
        except Exception as e:
            logger.error(f"Game creation error: {e}", exc_info=True)
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    # معالجة إجابات الألعاب
    if group_id in game_sessions:
        game = game_sessions[group_id]
        result = game.check_answer(text, user_id, user['name'])
        
        if result:
            responses = []
            
            if result.get('withdrawn'):
                return result.get('response')
            
            if result.get('game_over'):
                if group_id in game_sessions:
                    del game_sessions[group_id]
                if group_id in game_difficulties:
                    del game_difficulties[group_id]
                
                if result.get('points', 0) > 0 and user:
                    DB.add_points(user_id, result['points'], result.get('won', True), game.game_name)
            
            if result.get('response'):
                responses.append(result['response'])
            
            if result.get('next_question') and not result.get('game_over'):
                next_q = game.get_question()
                if next_q:
                    responses.append(next_q)
            
            return responses if len(responses) > 1 else (responses[0] if responses else None)
    
    return None

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()}), 200

@app.route('/')
def index():
    return "Bot 65 Enhanced - Running", 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
