from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, 
    ReplyMessageRequest, TextMessage, FlexMessage, 
    FlexContainer, QuickReply, QuickReplyItem, MessageAction
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

def get_quick_reply():
    """ازرار سريعة مرتبة: بداية أول زر، مساعدة آخر زر، بدون نص ونقاطي والصدارة"""
    return QuickReply(items=[
        QuickReplyItem(action=MessageAction(label="بداية", text="بداية")),    # أول زر
        QuickReplyItem(action=MessageAction(label="سؤال", text="سؤال")),      # الأكثر شيوعًا
        QuickReplyItem(action=MessageAction(label="تحدي", text="تحدي")),      # تفاعل ممتع
        QuickReplyItem(action=MessageAction(label="منشن", text="منشن")),      # تفاعل جماعي
        QuickReplyItem(action=MessageAction(label="اعتراف", text="اعتراف")),  # فضفضة واعترافات
        QuickReplyItem(action=MessageAction(label="اقتباس", text="اقتباس")), # محتوى ملهم
        QuickReplyItem(action=MessageAction(label="موقف", text="موقف")),      # مواقف للنقاش
        QuickReplyItem(action=MessageAction(label="شعر", text="شعر")),        # محتوى إبداعي
        QuickReplyItem(action=MessageAction(label="خاص", text="خاص")),        # محتوى خاص
        QuickReplyItem(action=MessageAction(label="مجهول", text="مجهول")),    # رسائل مجهولة
        QuickReplyItem(action=MessageAction(label="نصيحة", text="نصيحة")),    # نصائح خفيفة
        QuickReplyItem(action=MessageAction(label="العاب", text="العاب")),     # قسم الألعاب
        QuickReplyItem(action=MessageAction(label="مساعدة", text="مساعدة"))   # آخر زر
    ])

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
    
    # التعامل مع ادخال الاسم
    if user_id in waiting_for_name:
        if 2 <= len(text) <= 50:
            DB.register_user(user_id, text.strip())
            waiting_for_name.discard(user_id)
            msg = TextMessage(text=f"تم التسجيل بنجاح {text}")
            msg.quick_reply = get_quick_reply()
            return msg
        waiting_for_name.discard(user_id)
        msg = TextMessage(text="الاسم يجب ان يكون بين 2 و 50 حرف")
        msg.quick_reply = get_quick_reply()
        return msg
    
    # اوامر النصوص
text_commands = {
    'سؤال': 'questions',      # سؤال تفاعلي بين الأصدقاء
    'منشن': 'mentions',       # منشن للأصدقاء للتفاعل
    'تحدي': 'challenges',     # تحدي خفيف بين الأصدقاء
    'اعتراف': 'confessions',  # اعترافات بين الأصدقاء
    'اقتباس': 'quotes',       # اقتباس ملهم أو معبّر
    'موقف': 'situations',     # موقف يفتح باب النقاش
    'شعر': 'poem',            # بيت شعر أو مقطع قصير
    'خاص': 'private',         # أسئلة خاصة بين شخصين حبيبين
    'مجهول': 'anonymous',     # رسالة أو اعتراف بدون اسم
    'نصيحة': 'advice'         # نصيحة عامة وخفيفة
}
    
    if t in text_commands:
        msg = TextMessage(text=TextCommands.get_random(text_commands[t]))
        msg.quick_reply = get_quick_reply()
        return msg
    
    # قائمة النصوص
if t == 'نص':
    msg = TextMessage(
        text=(
            "اختر نوع النص:\n"
            "سؤال | منشن | تحدي | اعتراف | اقتباس | موقف | شعر | خاص | مجهول | نصيحة"
        )
    )
    msg.quick_reply = get_quick_reply()
    return msg
    
    # البداية
    if t in ['بداية', 'start']:
        if user:
            DB.update_activity(user_id)
        return FlexMessage(
            alt_text="Bot 65",
            contents=FlexContainer.from_dict(UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme))
        )
    
    # المساعدة
    if t in ['مساعدة', 'help']:
        return FlexMessage(
            alt_text="المساعدة",
            contents=FlexContainer.from_dict(UI.help_card(theme))
        )
    
    # الالعاب
    if t in ['العاب', 'ألعاب', 'الالعاب']:
        return FlexMessage(
            alt_text="الالعاب",
            contents=FlexContainer.from_dict(UI.games_menu(theme))
        )
    
    # التسجيل
    if t in ['تسجيل', 'تغيير']:
        waiting_for_name.add(user_id)
        msg = TextMessage(text="اكتب اسمك (2-50 حرف)")
        msg.quick_reply = get_quick_reply()
        return msg
    
    # النقاط
    if t == 'نقاطي':
        if not user:
            msg = TextMessage(text="يجب التسجيل اولا\nاكتب: تسجيل")
            msg.quick_reply = get_quick_reply()
            return msg
        DB.update_activity(user_id)
        return FlexMessage(
            alt_text="احصائياتك",
            contents=FlexContainer.from_dict(UI.stats(user, theme))
        )
    
    # الصدارة
    if t == 'الصدارة':
        leaders = DB.get_leaderboard()
        return FlexMessage(
            alt_text="الصدارة",
            contents=FlexContainer.from_dict(UI.leaderboard(leaders, theme))
        )
    
    # الثيم
    if t == 'ثيم':
        if not user:
            msg = TextMessage(text="يجب التسجيل اولا")
            msg.quick_reply = get_quick_reply()
            return msg
        new_theme = 'dark' if theme == 'light' else 'light'
        DB.set_theme(user_id, new_theme)
        user_themes[user_id] = new_theme
        msg = TextMessage(text=f"تم التغيير للثيم {'الداكن' if new_theme == 'dark' else 'الفاتح'}")
        msg.quick_reply = get_quick_reply()
        return msg
    
    # ايقاف او انسحاب
    if t in ['ايقاف', 'انسحب']:
        if group_id in game_sessions:
            game = game_sessions[group_id]
            # اذا انسحب اللاعب يتم اضافته لقائمة المنسحبين
            if t == 'انسحب' and user:
                game.withdrawn_users.add(user_id)
                return None  # لا يرد حتى لا يزعج القروب
            
            # ايقاف كامل للعبة
            del game_sessions[group_id]
            if group_id in game_difficulties:
                del game_difficulties[group_id]
            msg = TextMessage(text="تم ايقاف اللعبة")
            msg.quick_reply = get_quick_reply()
            return msg
        
        # اذا لم تكن هناك لعبة نشطة
        if t == 'انسحب':
            if user:
                DB.update_activity(user_id)
            return FlexMessage(
                alt_text="Bot 65",
                contents=FlexContainer.from_dict(UI.welcome(user['name'] if user else 'مستخدم', bool(user), theme))
            )
        return None
    
    # تعيين الصعوبة
    if t.startswith('صعوبة ') or t.startswith('مستوى '):
        try:
            level = int(t.split()[-1])
            if 1 <= level <= 5:
                game_difficulties[group_id] = level
                msg = TextMessage(text=f"تم تعيين الصعوبة: مستوى {level}")
                msg.quick_reply = get_quick_reply()
                return msg
        except:
            pass
        msg = TextMessage(text="استخدم: صعوبة 1 (الى 5)")
        msg.quick_reply = get_quick_reply()
        return msg
    
    # يجب ان يكون مسجلا للعب
    if not user:
        return None
    
    # بدء الالعاب
    game_map = {
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
    
    if t in game_map:
        try:
            game_class = game_map[t]
            difficulty = game_difficulties.get(group_id, 3)
            game = game_class(line_api, difficulty=difficulty, theme=theme)
            game_sessions[group_id] = game
            return game.start_game()
        except Exception as e:
            logger.error(f"Game creation error: {e}", exc_info=True)
            msg = TextMessage(text="حدث خطأ في بدء اللعبة")
            msg.quick_reply = get_quick_reply()
            return msg
    
    # التعامل مع اجابات الالعاب
    if group_id in game_sessions:
        game = game_sessions[group_id]
        
        # تجاهل اجابات المنسحبين
        if user_id in game.withdrawn_users:
            return None
        
        result = game.check_answer(text, user_id, user['name'])
        
        if result:
            if result.get('withdrawn'):
                return None  # لا يرد عند الانسحاب
            
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
