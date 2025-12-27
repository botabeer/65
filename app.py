from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, 
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_TOKEN or not LINE_SECRET:
    logger.error("بيانات الاعتماد مفقودة")
    sys.exit(1)

configuration = Configuration(access_token=LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

from database import DB
from ui import UI
from text_commands import TextCommands
from games import (
    CategoryGame, FastGame, CompatibilityGame, SongGame,
    OppositeGame, ChainGame, LettersGame, RiddleGame,
    ScrambleGame, MafiaGame, WordColorGame, RouletteGame, LetterGame
)

DB.init()
TextCommands.load_all()

game_sessions = {}
waiting_for_name = set()
user_themes = {}

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
    'فئه': CategoryGame,
    'اسرع': FastGame,
    'توافق': CompatibilityGame,
    'اغنيه': SongGame,
    'ضد': OppositeGame,
    'سلسله': ChainGame,
    'تكوين': LettersGame,
    'لغز': RiddleGame,
    'ترتيب': ScrambleGame,
    'مافيا': MafiaGame,
    'لون': WordColorGame,
    'روليت': RouletteGame,
    'حرف': LetterGame
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"خطأ في الويب هوك: {e}")
    
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        user_id = event.source.user_id
        text = event.message.text.strip()
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        try:
            response = process_message(text, user_id, group_id, line_api)
            if response:
                messages = response if isinstance(response, list) else [response]
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=messages
                    )
                )
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

def process_message(text, user_id, group_id, line_api):
    normalized_text = text.lower().strip()
    user = DB.get_user(user_id)
    theme = user_themes.get(user_id, user['theme'] if user else 'light')
    
    if user_id in waiting_for_name:
        return handle_name_registration(text, user_id)
    
    if normalized_text in TEXT_COMMANDS:
        content = TextCommands.get_random(TEXT_COMMANDS[normalized_text])
        msg = TextMessage(text=content)
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if normalized_text in ['بداية', 'start', 'ابدا']:
        if user:
            DB.update_activity(user_id)
        return create_welcome_message(user, theme)
    
    if normalized_text in ['مساعدة', 'help', 'مساعده']:
        return FlexMessage(
            alt_text="المساعدة",
            contents=FlexContainer.from_dict(UI.help_card(theme))
        )
    
    if normalized_text in ['نص', 'نصوص']:
        return FlexMessage(
            alt_text="قائمة النصوص",
            contents=FlexContainer.from_dict(UI.text_commands_menu(theme))
        )
    
    if normalized_text in ['العاب', 'ألعاب', 'الالعاب']:
        return FlexMessage(
            alt_text="الالعاب",
            contents=FlexContainer.from_dict(UI.games_menu(theme))
        )
    
    if normalized_text in ['تسجيل', 'تغيير']:
        waiting_for_name.add(user_id)
        msg = TextMessage(text="اكتب اسمك الان")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    if normalized_text == 'نقاطي':
        if not user:
            return create_error_message("يجب التسجيل اولا - اكتب: تسجيل")
        DB.update_activity(user_id)
        return FlexMessage(
            alt_text="احصائياتك",
            contents=FlexContainer.from_dict(UI.stats(user, theme))
        )
    
    if normalized_text in ['الصدارة', 'صدارة']:
        leaders = DB.get_leaderboard()
        return FlexMessage(
            alt_text="الصدارة",
            contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme))
        )
    
    if normalized_text == 'ثيم':
        if not user:
            return create_error_message("يجب التسجيل اولا")
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        user_themes[user_id] = new_theme
        theme_name = 'الداكن' if new_theme == 'dark' else 'الفاتح'
        return create_success_message(f"تم التغيير للثيم {theme_name}")
    
    if normalized_text in ['ايقاف', 'انسحب']:
        return handle_game_stop(group_id, user_id, user, normalized_text, theme)
    
    if not user:
        return None
    
    if normalized_text in GAME_MAP:
        return start_game(normalized_text, group_id, line_api, theme)
    
    if group_id in game_sessions:
        return handle_game_answer(group_id, text, user_id, user)
    
    return None

def handle_name_registration(name, user_id):
    name = name.strip()
    if 1 <= len(name) <= 20:
        DB.register_user(user_id, name)
        waiting_for_name.discard(user_id)
        user = DB.get_user(user_id)
        msg = FlexMessage(
            alt_text="تم التسجيل",
            contents=FlexContainer.from_dict(
                UI.welcome(name, True, user['theme'])
            )
        )
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    waiting_for_name.discard(user_id)
    return create_error_message("الاسم يجب ان يكون بين 1 و 20 حرف")

def create_welcome_message(user, theme):
    name = user['name'] if user else 'مستخدم'
    is_registered = bool(user)
    msg = FlexMessage(
        alt_text="Bot 65",
        contents=FlexContainer.from_dict(
            UI.welcome(name, is_registered, theme)
        )
    )
    msg.quick_reply = UI.get_quick_reply()
    return msg

def create_error_message(text):
    msg = TextMessage(text=text)
    msg.quick_reply = UI.get_quick_reply()
    return msg

def create_success_message(text):
    msg = TextMessage(text=text)
    msg.quick_reply = UI.get_quick_reply()
    return msg

def handle_game_stop(group_id, user_id, user, command, theme):
    if group_id in game_sessions:
        game = game_sessions[group_id]
        if command == 'انسحب' and user:
            game.withdrawn_users.add(user_id)
            return None
        del game_sessions[group_id]
        return create_success_message("تم ايقاف اللعبة")
    
    if command == 'انسحب' and user:
        DB.update_activity(user_id)
        return create_welcome_message(user, theme)
    
    return None

def start_game(game_type, group_id, line_api, theme):
    try:
        game_class = GAME_MAP[game_type]
        game = game_class(line_api, theme=theme)
        game_sessions[group_id] = game
        return game.start_game()
    except Exception as e:
        logger.error(f"خطأ في بدء اللعبة {game_type}: {e}", exc_info=True)
        return create_error_message("حدث خطأ في بدء اللعبة")

def handle_game_answer(group_id, text, user_id, user):
    game = game_sessions[group_id]
    
    if user_id in game.withdrawn_users:
        return None
    
    result = game.check_answer(text, user_id, user['name'])
    
    if not result:
        return None
    
    # التعامل مع النتائج المختلفة
    if isinstance(result, (TextMessage, FlexMessage)):
        return result
    
    if not isinstance(result, dict):
        return None
    
    # التحقق من الانسحاب
    if result.get('withdrawn'):
        return None
    
    # التحقق من نهاية اللعبة
    if result.get('game_over'):
        if group_id in game_sessions:
            del game_sessions[group_id]
        
        points = result.get('points', 0)
        if points > 0:
            won = result.get('won', True)
            DB.add_points(user_id, points, won, game.game_name)
    
    return result.get('response')

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'time': datetime.now().isoformat()
    }), 200

@app.route('/')
def index():
    return "Bot 65 - Running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
