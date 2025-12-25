"""
Bot 65 - LINE Games Bot
"""
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
    theme = user['theme'] if user else 'light'
    
    if user_id in waiting_for_name:
        if 2 <= len(text) <= 50:
            DB.register_user(user_id, text.strip())
            waiting_for_name.discard(user_id)
            return TextMessage(text=f"تم التسجيل: {text}")
        waiting_for_name.discard(user_id)
        return None
    
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
    
    if t in ['بداية', 'start', 'بدايه']:
        if user:
            DB.update_activity(user_id)
        return FlexMessage(alt_text="Bot 65", contents=FlexContainer.from_dict(
            UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme)))
    
    if t in ['مساعدة', 'help', 'مساعده']:
        return FlexMessage(alt_text="المساعدة", contents=FlexContainer.from_dict(UI.help_card(theme)))
    
    if t in ['العاب', 'ألعاب', 'الالعاب']:
        return FlexMessage(alt_text="الألعاب", contents=FlexContainer.from_dict(UI.games_menu(theme)))
    
    if t in ['تسجيل', 'تغيير']:
        waiting_for_name.add(user_id)
        return TextMessage(text="اكتب اسمك (2-50 حرف)")
    
    if t in ['نقاطي', 'احصائياتي']:
        if not user:
            return TextMessage(text="يجب التسجيل اولا")
        DB.update_activity(user_id)
        return FlexMessage(alt_text="احصائياتك", contents=FlexContainer.from_dict(UI.stats(user, theme)))
    
    if t in ['الصدارة', 'المتصدرين', 'الصداره']:
        leaders = DB.get_leaderboard()
        return FlexMessage(alt_text="الصدارة", contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme)))
    
    if t == 'ثيم':
        if not user:
            return TextMessage(text="يجب التسجيل اولا")
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        return TextMessage(text=f"تم للثيم {'الداكن' if new_theme == 'dark' else 'الفاتح'}")
    
    if t in ['ايقاف', 'stop', 'إيقاف', 'انسحب']:
        if group_id in game_sessions:
            del game_sessions[group_id]
            return TextMessage(text="تم ايقاف اللعبة")
        return None
    
    if not user:
        return None
    
    game_map = {
        'اغنيه': 'SongGame', 'ضد': 'OppositeGame', 'سلسله': 'ChainGame',
        'اسرع': 'FastGame', 'تكوين': 'LettersGame', 'فئه': 'CategoryGame',
        'لعبه': 'HumanAnimalGame', 'توافق': 'CompatibilityGame', 
        'ذكاء': 'IqGame', 'خمن': 'GuessGame', 'ترتيب': 'ScrambleGame',
        'لون': 'WordColorGame', 'روليت': 'RouletteGame', 
        'سين': 'SeenJeemGame', 'حروف': 'LetterGame', 'مافيا': 'MafiaGame'
    }
    
    if t in game_map:
        try:
            from games import (
                SongGame, OppositeGame, ChainGame, FastGame,
                LettersGame, CategoryGame, HumanAnimalGame,
                CompatibilityGame, IqGame, GuessGame, ScrambleGame,
                WordColorGame, RouletteGame, SeenJeemGame, LetterGame,
                MafiaGame
            )
            
            game_classes = {
                'SongGame': SongGame, 'OppositeGame': OppositeGame, 
                'ChainGame': ChainGame, 'FastGame': FastGame,
                'LettersGame': LettersGame, 'CategoryGame': CategoryGame,
                'HumanAnimalGame': HumanAnimalGame, 'CompatibilityGame': CompatibilityGame,
                'IqGame': IqGame, 'GuessGame': GuessGame, 'ScrambleGame': ScrambleGame,
                'WordColorGame': WordColorGame, 'RouletteGame': RouletteGame,
                'SeenJeemGame': SeenJeemGame, 'LetterGame': LetterGame,
                'MafiaGame': MafiaGame
            }
            
            game_class = game_classes.get(game_map[t])
            if game_class:
                game = game_class(line_api)
                game_sessions[group_id] = game
                return game.start_game()
        except Exception as e:
            logger.error(f"Game creation error: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    if group_id in game_sessions:
        game = game_sessions[group_id]
        result = game.check_answer(text, user_id, user['name'])
        
        if result:
            if result.get('game_over'):
                del game_sessions[group_id]
                if result.get('points', 0) > 0:
                    DB.add_points(user_id, result['points'], result.get('won', True), game.game_name)
            
            responses = []
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
    return "Bot 65 Running", 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
