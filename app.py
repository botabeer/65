from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, 
    ReplyMessageRequest, TextMessage, FlexMessage, 
    FlexContainer
)
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
from games import (
    GuessGame, FastGame, CompatibilityGame, SongGame,
    OppositeGame, ChainGame, LettersGame, CategoryGame,
    HumanAnimalGame, IqGame, ScrambleGame, LetterGame,
    MafiaGame, WordColorGame, RouletteGame, SeenJeemGame
)

DB.init()
TextCommands.load_all()

game_sessions = {}
waiting_for_name = set()
user_themes = {}
game_difficulties = {}

TEXT_COMMANDS = {
    'سؤال': 'questions',
    'منشن': 'mentions',
    'تحدي': 'challenges',
    'اعتراف': 'confessions',
    'اقتباس': 'quotes',
    'موقف': 'situations',
    'شعر': 'poem',
    'خاص': 'private',
    'مجهول': 'anonymous',
    'نصيحة': 'advice'
}

GAME_MAP = {
    'خمن': GuessGame,
    'اسرع': FastGame,
    'توافق': CompatibilityGame,
    'اغنيه': SongGame,
    'ضد': OppositeGame,
    'سلسله': ChainGame,
    'تكوين': LettersGame,
    'فئه': CategoryGame,
    'لعبه': HumanAnimalGame,
    'ذكاء': IqGame,
    'ترتيب': ScrambleGame,
    'حروف': LetterGame,
    'مافيا': MafiaGame,
    'لون': WordColorGame,
    'روليت': RouletteGame,
    'سين': SeenJeemGame
}

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
                line_api.reply_message(ReplyMessageRequest(
                    reply_token=event.reply_token, 
                    messages=msgs
                ))
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

def process(text, user_id, group_id, line_api):
    t = text.lower().strip()
    user = DB.get_user(user_id)
    theme = user_themes.get(user_id, user['theme'] if user else 'light')
    
    if user_id in waiting_for_name:
        if 2 <= len(text) <= 50:
            DB.register_user(user_id, text.strip())
            waiting_for_name.discard(user_id)
            msg = TextMessage(text=f"تم التسجيل بنجاح {text}")
            msg.quick_reply = UI.get_quick_reply()
            return msg
        waiting_for_name.discard(user_id)
        msg = TextMessage(text="الاسم يجب ان يكون بين 2 و 50 حرف")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if t in TEXT_COMMANDS:
        msg = TextMessage(text=TextCommands.get_random(TEXT_COMMANDS[t]))
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if t == 'نص':
        msg = TextMessage(text="اختر نوع النص:\nسؤال - منشن - تحدي - اعتراف - اقتباس - موقف - شعر - خاص - مجهول - نصيحة")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if t in ['بداية', 'start']:
        if user:
            DB.update_activity(user_id)
        return FlexMessage(
            alt_text="Bot 65",
            contents=FlexContainer.from_dict(UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme))
        )
    
    if t in ['مساعدة', 'help']:
        return FlexMessage(alt_text="المساعدة", contents=FlexContainer.from_dict(UI.help_card(theme)))
    
    if t in ['العاب', 'ألعاب', 'الالعاب']:
        return FlexMessage(alt_text="الالعاب", contents=FlexContainer.from_dict(UI.games_menu(theme)))
    
    if t in ['تسجيل', 'تغيير']:
        waiting_for_name.add(user_id)
        msg = TextMessage(text="اكتب اسمك (2-50 حرف)")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if t == 'نقاطي':
        if not user:
            msg = TextMessage(text="يجب التسجيل اولا\nاكتب: تسجيل")
            msg.quick_reply = UI.get_quick_reply()
            return msg
        DB.update_activity(user_id)
        return FlexMessage(alt_text="احصائياتك", contents=FlexContainer.from_dict(UI.stats(user, theme)))
    
    if t == 'الصدارة':
        leaders = DB.get_leaderboard()
        return FlexMessage(alt_text="الصدارة", contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme)))
    
    if t == 'ثيم':
        if not user:
            msg = TextMessage(text="يجب التسجيل اولا")
            msg.quick_reply = UI.get_quick_reply()
            return msg
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        user_themes[user_id] = new_theme
        msg = TextMessage(text=f"تم التغيير للثيم {'الداكن' if new_theme == 'dark' else 'الفاتح'}")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if t in ['ايقاف', 'انسحب']:
        if group_id in game_sessions:
            game = game_sessions[group_id]
            if t == 'انسحب' and user:
                game.withdrawn_users.add(user_id)
                return None
            
            del game_sessions[group_id]
            if group_id in game_difficulties:
                del game_difficulties[group_id]
            msg = TextMessage(text="تم ايقاف اللعبة")
            msg.quick_reply = UI.get_quick_reply()
            return msg
        
        if t == 'انسحب' and user:
            DB.update_activity(user_id)
            return FlexMessage(alt_text="Bot 65", contents=FlexContainer.from_dict(UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme)))
        return None
    
    if t.startswith('صعوبة ') or t.startswith('مستوى '):
        try:
            level = int(t.split()[-1])
            if 1 <= level <= 5:
                game_difficulties[group_id] = level
                msg = TextMessage(text=f"تم تعيين الصعوبة: مستوى {level}")
                msg.quick_reply = UI.get_quick_reply()
                return msg
        except:
            pass
        msg = TextMessage(text="استخدم: صعوبة 1 (الى 5)")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if not user:
        return None
    
    if t in GAME_MAP:
        try:
            game_class = GAME_MAP[t]
            difficulty = game_difficulties.get(group_id, 3)
            game = game_class(line_api, difficulty=difficulty, theme=theme)
            game_sessions[group_id] = game
            return game.start_game()
        except Exception as e:
            logger.error(f"Game creation error: {e}", exc_info=True)
            msg = TextMessage(text="حدث خطأ في بدء اللعبة")
            msg.quick_reply = UI.get_quick_reply()
            return msg
    
    if group_id in game_sessions:
        game = game_sessions[group_id]
        
        if user_id in game.withdrawn_users:
            return None
        
        result = game.check_answer(text, user_id, user['name'])
        
        if result:
            if result.get('withdrawn'):
                return None
            
            if result.get('game_over'):
                if group_id in game_sessions:
                    del game_sessions[group_id]
                if group_id in game_difficulties:
                    del game_difficulties[group_id]
                
                if result.get('points', 0) > 0 and user:
                    DB.add_points(user_id, result['points'], result.get('won', True), game.game_name)
            
            return result.get('response')
    
    return None

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()}), 200

@app.route('/')
def index():
    return "Bot 65 - Running", 200

port = int(os.environ.get("PORT", 10000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
