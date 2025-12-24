"""
Bot 65 - بوت ألعاب LINE
تطبيق رئيسي شامل
"""
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os, sys, logging
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
from games import GameEngine
from ui import UI
from text_commands import TextCommands

DB.init()
TextCommands.load_all()

game_sessions = {}
waiting_for_name = set()

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
            response = process(text, user_id, group_id)
            if response:
                msgs = response if isinstance(response, list) else [response]
                line_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=msgs))
        except Exception as e:
            logger.error(f"Error: {e}")

def process(text, user_id, group_id):
    t = text.lower().strip()
    user = DB.get_user(user_id)
    theme = user['theme'] if user else 'light'
    
    if user_id in waiting_for_name:
        if 2 <= len(text) <= 50:
            DB.register_user(user_id, text.strip())
            waiting_for_name.discard(user_id)
            return TextMessage(text=f"تم التسجيل: {text}")
        waiting_for_name.discard(user_id)
        return None
    
    if t in ['سؤال','سوال']:
        return TextMessage(text=TextCommands.get_random('questions'))
    if t == 'تحدي':
        return TextMessage(text=TextCommands.get_random('challenges'))
    if t == 'اعتراف':
        return TextMessage(text=TextCommands.get_random('confessions'))
    if t == 'منشن':
        return TextMessage(text=TextCommands.get_random('mentions'))
    if t in ['حكمة','حكمه']:
        return TextMessage(text=TextCommands.get_random('quotes'))
    if t == 'موقف':
        return TextMessage(text=TextCommands.get_random('situations'))
    
    if t in ['بداية','start','بدايه']:
        if user:
            DB.update_activity(user_id)
        return FlexMessage(alt_text="Bot 65", contents=FlexContainer.from_dict(
            UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme)))
    
    if t in ['مساعدة','help','مساعده']:
        return FlexMessage(alt_text="المساعدة", contents=FlexContainer.from_dict(UI.help_card(theme)))
    
    if t in ['العاب','ألعاب']:
        return FlexMessage(alt_text="الألعاب", contents=FlexContainer.from_dict(UI.games_menu(theme)))
    
    if t in ['تسجيل','تغيير']:
        waiting_for_name.add(user_id)
        return TextMessage(text="اكتب اسمك (2-50 حرف)")
    
    if t in ['نقاطي','احصائياتي']:
        if not user:
            return None
        DB.update_activity(user_id)
        return FlexMessage(alt_text="احصائياتك", contents=FlexContainer.from_dict(UI.stats(user, theme)))
    
    if t in ['الصدارة','المتصدرين','الصداره']:
        leaders = DB.get_leaderboard()
        return FlexMessage(alt_text="الصدارة", contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme)))
    
    if t == 'ثيم':
        if not user:
            return None
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        return TextMessage(text=f"تم للثيم {'الداكن' if new_theme == 'dark' else 'الفاتح'}")
    
    if t in ['ايقاف','stop','إيقاف','انسحب']:
        if group_id in game_sessions:
            game = game_sessions[group_id]
            if not hasattr(game, 'withdrawn'):
                game.withdrawn = set()
            game.withdrawn.add(user_id)
        return None
    
    if not user:
        return None
    
    if t in GameEngine.GAMES:
        game = GameEngine.create(t, theme)
        game.withdrawn = set()
        game_sessions[group_id] = game
        return game.start()
    
    if group_id in game_sessions:
        game = game_sessions[group_id]
        if hasattr(game, 'withdrawn') and user_id in game.withdrawn:
            return None
        
        result = game.play(text, user_id, user['name'])
        if result.get('game_over'):
            del game_sessions[group_id]
            if result.get('points', 0) > 0:
                DB.add_points(user_id, result['points'], result.get('won', True), game.name)
        return result.get('response')
    
    return None

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()}), 200

@app.route('/')
def index():
    return "Bot 65 Running", 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
