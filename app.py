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
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
    CategoryGame, FastGame, CompatibilityGame, SongGame,
    OppositeGame, ChainGame, LettersGame, RiddleGame,
    ScrambleGame, MafiaGame, WordColorGame, LetterGame
)

# Initialize database and load text commands
DB.init()
TextCommands.load_all()

# Game sessions and user state
game_sessions = {}
waiting_for_name = set()
user_themes = {}
silent_users = set()

# Text commands mapping
TEXT_COMMANDS = {
    'سؤال': 'questions',
    'منشن': 'mentions',
    'تحدي': 'challenges',
    'اعتراف': 'confessions',
    'اقتباس': 'quotes',
    'موقف': 'situations',
    'خاص': 'private',
    'مجهول': 'anonymous',
    'نصيحة': 'advice',
    'شعر': 'poem'
}

# Game mapping (بدون روليت)
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
    'حرف': LetterGame
}

# Auto-cleanup scheduler
scheduler = BackgroundScheduler()

def cleanup_inactive_users():
    """Remove inactive users after 7 days"""
    try:
        deleted = DB.cleanup_inactive_users(days=7)
        logger.info(f"Cleanup: Removed {deleted} inactive users")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

scheduler.add_job(cleanup_inactive_users, 'cron', hour=3, minute=0)
scheduler.start()

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
            logger.error(f"Message processing error: {e}", exc_info=True)

def process_message(text, user_id, group_id, line_api):
    normalized_text = text.lower().strip()
    
    # Check if user is in silent mode
    if user_id in silent_users:
        if normalized_text in ['تسجيل', 'بداية', 'start', 'ابدا']:
            silent_users.discard(user_id)
            logger.info(f"User {user_id} reactivated from silent mode")
        else:
            logger.info(f"Ignoring message from silent user {user_id}")
            return None
    
    user = DB.get_user(user_id)
    theme = user_themes.get(user_id, user['theme'] if user else 'light')
    
    # Handle name registration
    if user_id in waiting_for_name:
        return handle_name_registration(text, user_id)
    
    # Text commands
    if normalized_text in TEXT_COMMANDS:
        content = TextCommands.get_random(TEXT_COMMANDS[normalized_text])
        msg = TextMessage(text=content)
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    # Start command
    if normalized_text in ['بداية', 'start', 'ابدا']:
        if user:
            DB.update_activity(user_id)
        return create_welcome_message(user, theme)
    
    # Help command
    if normalized_text in ['مساعدة', 'help', 'مساعده']:
        return FlexMessage(
            alt_text="Help",
            contents=FlexContainer.from_dict(UI.help_card(theme))
        )
    
    # Text commands menu
    if normalized_text in ['نص', 'نصوص']:
        return FlexMessage(
            alt_text="Text Commands",
            contents=FlexContainer.from_dict(UI.text_commands_menu(theme))
        )
    
    # Games menu
    if normalized_text in ['العاب', 'ألعاب', 'الالعاب']:
        return FlexMessage(
            alt_text="Games",
            contents=FlexContainer.from_dict(UI.games_menu(theme))
        )
    
    # Registration
    if normalized_text in ['تسجيل', 'تغيير']:
        silent_users.discard(user_id)
        waiting_for_name.add(user_id)
        msg = TextMessage(text="اكتب اسمك الان")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    # Stats
    if normalized_text == 'نقاطي':
        if not user:
            return create_error_message("يجب التسجيل اولا - اكتب: تسجيل")
        DB.update_activity(user_id)
        return FlexMessage(
            alt_text="Your Stats",
            contents=FlexContainer.from_dict(UI.stats(user, theme))
        )
    
    # Leaderboard
    if normalized_text in ['الصدارة', 'صدارة']:
        leaders = DB.get_leaderboard()
        return FlexMessage(
            alt_text="Leaderboard",
            contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme))
        )
    
    # Theme toggle
    if normalized_text == 'ثيم':
        if not user:
            return create_error_message("يجب التسجيل اولا")
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        user_themes[user_id] = new_theme
        theme_name = 'الداكن' if new_theme == 'dark' else 'الفاتح'
        return create_success_message(f"تم التغيير للثيم {theme_name}")
    
    # Withdraw
    if normalized_text == 'انسحب':
        if group_id in game_sessions:
            game = game_sessions[group_id]
            game.withdrawn_users.add(user_id)
        
        silent_users.add(user_id)
        logger.info(f"User {user_id} entered silent mode")
        
        msg = TextMessage(text="تم الانسحاب - لن يتم احتساب اجاباتك\nللعودة اضغط: تسجيل")
        msg.quick_reply = UI.get_quick_reply()
        return msg
    
    # Stop game
    if normalized_text == 'ايقاف':
        if group_id in game_sessions:
            del game_sessions[group_id]
            return create_success_message("تم ايقاف اللعبة")
        return None
    
    # Must be registered to play
    if not user:
        return None
    
    # Start game
    if normalized_text in GAME_MAP:
        return start_game(normalized_text, group_id, line_api, theme)
    
    # Handle game answer
    if group_id in game_sessions:
        return handle_game_answer(group_id, text, user_id, user)
    
    return None

def handle_name_registration(name, user_id):
    name = name.strip()
    if 1 <= len(name) <= 20:
        DB.register_user(user_id, name)
        waiting_for_name.discard(user_id)
        silent_users.discard(user_id)
        
        user = DB.get_user(user_id)
        msg = FlexMessage(
            alt_text="Registration Complete",
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

def start_game(game_type, group_id, line_api, theme):
    try:
        game_class = GAME_MAP[game_type]
        game = game_class(line_api, theme=theme)
        game_sessions[group_id] = game
        return game.start_game()
    except Exception as e:
        logger.error(f"Game start error {game_type}: {e}", exc_info=True)
        return create_error_message("حدث خطأ في بدء اللعبة")

def handle_game_answer(group_id, text, user_id, user):
    game = game_sessions[group_id]
    
    if user_id in game.withdrawn_users:
        return None
    
    result = game.check_answer(text, user_id, user['name'])
    
    if not result:
        return None
    
    if isinstance(result, (TextMessage, FlexMessage)):
        return result
    
    if not isinstance(result, dict):
        return None
    
    if result.get('withdrawn'):
        return None
    
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
        'time': datetime.now().isoformat(),
        'users': DB.get_stats(),
        'silent_users': len(silent_users)
    }), 200

@app.route('/')
def index():
    return "Bot 65 - Running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
