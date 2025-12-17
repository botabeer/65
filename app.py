import logging
from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, QuickReply, QuickReplyItem, MessageAction
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from config import Config
from database import Database
from game_manager import GameManager
from text_manager import TextManager
from ui import UI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
line_config = Configuration(access_token=Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

db = Database()
game_mgr = GameManager(db)
text_mgr = TextManager()

executor = ThreadPoolExecutor(max_workers=Config.WORKERS, thread_name_prefix="worker")

scheduler = BackgroundScheduler(timezone=pytz.UTC)
scheduler.add_job(func=lambda: db.cleanup_memory(), trigger="interval", minutes=30)
scheduler.start()

def get_quick_reply():
    items = []
    commands = [
        "بداية", "العاب", "نقاطي", "الصدارة", "انجازات", "مكافأة",
        "ثيم", "ايقاف", "مساعدة", "تحدي", "سؤال", "اعتراف",
        "منشن", "موقف", "حكمة", "شخصية"
    ]
    for cmd in commands:
        items.append(QuickReplyItem(action=MessageAction(label=cmd, text=cmd)))
    return QuickReply(items=items)

def reply_message(reply_token, messages):
    if not isinstance(messages, list):
        messages = [messages]
    safe_messages = [m for m in messages if m][:5]
    try:
        with ApiClient(line_config) as client:
            MessagingApi(client).reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=safe_messages)
            )
    except Exception as e:
        logger.error(f"Reply error: {e}")

def process_message(user_id, text, reply_token):
    try:
        normalized = Config.normalize(text)
        
        if db.is_waiting_name(user_id):
            if len(text) < Config.MIN_NAME_LENGTH or len(text) > Config.MAX_NAME_LENGTH:
                reply_message(reply_token, TextMessage(text=f"الاسم يجب أن يكون بين {Config.MIN_NAME_LENGTH} و {Config.MAX_NAME_LENGTH} حرف"))
                return
            db.register_user(user_id, text)
            db.clear_waiting_name(user_id)
            user = db.get_user(user_id)
            reply_message(reply_token, [
                TextMessage(text=f"مرحبا {text}! تم تسجيلك بنجاح"),
                UI.main_menu(user, db)
            ])
            return
        
        if db.is_changing_name(user_id):
            if len(text) < Config.MIN_NAME_LENGTH or len(text) > Config.MAX_NAME_LENGTH:
                reply_message(reply_token, TextMessage(text=f"الاسم يجب أن يكون بين {Config.MIN_NAME_LENGTH} و {Config.MAX_NAME_LENGTH} حرف"))
                return
            db.update_name(user_id, text)
            db.clear_changing_name(user_id)
            reply_message(reply_token, TextMessage(text=f"تم تغيير اسمك إلى: {text}"))
            return
        
        if not db.is_registered(user_id):
            if normalized in ["تسجيل", "بدايه", "بداية"]:
                db.set_waiting_name(user_id)
                reply_message(reply_token, TextMessage(text="اكتب اسمك للتسجيل:"))
            else:
                reply_message(reply_token, TextMessage(text="مرحبا! اكتب 'تسجيل' للبدء"))
            return
        
        db.update_activity(user_id)
        user = db.get_user(user_id)
        
        if normalized == "انسحب":
            db.unregister(user_id)
            reply_message(reply_token, TextMessage(text="تم حذف حسابك بنجاح. اكتب 'تسجيل' للعودة"))
            return
        
        if db.has_active_game(user_id):
            if normalized == "ايقاف":
                score = game_mgr.stop_game(user_id)
                reply_message(reply_token, TextMessage(
                    text=f"تم إيقاف اللعبة. حصلت على {score} نقطة",
                    quickReply=get_quick_reply()
                ))
                return
            
            if normalized == "تلميح":
                hint_msg = game_mgr.get_hint(user_id)
                if hint_msg:
                    reply_message(reply_token, hint_msg)
                else:
                    reply_message(reply_token, TextMessage(text="التلميحات غير متوفرة"))
                return
            
            if normalized in ["الاجابه", "الإجابة", "اجابه", "إجابة"]:
                reveal_msg = game_mgr.reveal_answer(user_id)
                if reveal_msg:
                    reply_message(reply_token, reveal_msg)
                else:
                    reply_message(reply_token, TextMessage(text="عرض الإجابة غير متوفر"))
                return
            
            result, correct = game_mgr.process_answer(user_id, text)
            
            if result and result.get("finished"):
                score = result['score']
                total = result['total']
                game_name = result['game_name']
                achievements = result.get('achievements', [])
                
                status = "ممتاز! فوز مثالي" if score == total else f"جيد! {score}/{total}"
                msg = f"{game_name}\n{status}\nالنقاط: +{score}"
                
                messages = [TextMessage(text=msg, quickReply=get_quick_reply())]
                
                for achievement in achievements:
                    messages.append(UI.achievement_unlocked(achievement, user['theme']))
                
                reply_message(reply_token, messages)
            else:
                feedback = "صحيح" if correct else f"خطأ. الإجابة: {game_mgr.db.get_game_progress(user_id).current_answer if not correct else ''}"
                messages = [TextMessage(text=feedback)]
                if result:
                    messages.append(result)
                reply_message(reply_token, messages)
            return
        
        if normalized in ["بدايه", "بداية", "القائمه", "القائمة"]:
            reply_message(reply_token, UI.main_menu(user, db))
        
        elif normalized == "العاب":
            reply_message(reply_token, UI.games_list(user['theme']))
        
        elif normalized in ["نقاطي", "احصائياتي", "إحصائياتي"]:
            win_rate = (user['wins'] / user['games'] * 100) if user['games'] > 0 else 0
            msg = f"اسم: {user['name']}\nنقاط: {user['points']}\nألعاب: {user['games']}\nانتصارات: {user['wins']}\nنسبة الفوز: {win_rate:.1f}%\nسلسلة: {user['streak']}\nأفضل سلسلة: {user['best_streak']}"
            reply_message(reply_token, TextMessage(text=msg, quickReply=get_quick_reply()))
        
        elif normalized in ["الصداره", "الصدارة"]:
            leaders = db.get_leaderboard(10)
            reply_message(reply_token, UI.leaderboard(leaders, user['theme']))
        
        elif normalized in ["انجازات", "إنجازات"]:
            user_achievements = db.get_user_achievements(user_id)
            reply_message(reply_token, UI.achievements_list(user_achievements, user['theme']))
        
        elif normalized in ["مكافأة", "مكافاة"]:
            if db.claim_reward(user_id):
                reply_message(reply_token, TextMessage(
                    text=f"تم! حصلت على +{Config.DAILY_REWARD_POINTS} نقطة",
                    quickReply=get_quick_reply()
                ))
            else:
                reply_message(reply_token, TextMessage(
                    text=f"يمكنك الحصول على المكافأة كل {Config.DAILY_REWARD_HOURS} ساعة",
                    quickReply=get_quick_reply()
                ))
        
        elif normalized == "ثيم":
            new_theme = "dark" if user['theme'] == "light" else "light"
            db.change_theme(user_id, new_theme)
            reply_message(reply_token, TextMessage(
                text=f"تم تغيير الثيم إلى: {'الداكن' if new_theme == 'dark' else 'الفاتح'}",
                quickReply=get_quick_reply()
            ))
        
        elif normalized in ["مساعده", "مساعدة", "help"]:
            help_text = """Bot Mesh - بوت ألعاب عربي

الأوامر الأساسية:
• بداية - القائمة الرئيسية
• العاب - قائمة الألعاب
• نقاطي - إحصائياتك
• الصدارة - أفضل اللاعبين
• انجازات - إنجازاتك
• مكافأة - مكافأة يومية
• ثيم - تغيير الثيم
• ايقاف - إيقاف اللعبة

الألعاب المتوفرة:
ذكاء، خمن، رياضيات، ترتيب، ضد، كتابه، سلسله، انسان، كلمات، اغنيه، الوان، توافق

محتوى إضافي:
تحدي، سؤال، اعتراف، منشن، موقف، حكمة، شخصية"""
            reply_message(reply_token, TextMessage(text=help_text, quickReply=get_quick_reply()))
        
        elif normalized in game_mgr.game_mappings:
            question = game_mgr.start_game(user_id, normalized, user['theme'])
            if question:
                reply_message(reply_token, question)
            else:
                reply_message(reply_token, TextMessage(text="خطأ في بدء اللعبة", quickReply=get_quick_reply()))
        
        elif normalized in text_mgr.cmd_mapping:
            content = text_mgr.get_content(normalized)
            if content:
                reply_message(reply_token, TextMessage(text=content, quickReply=get_quick_reply()))
        
        else:
            reply_message(reply_token, TextMessage(
                text="أمر غير معروف. اكتب 'مساعدة' لعرض الأوامر",
                quickReply=get_quick_reply()
            ))
    
    except Exception as e:
        logger.exception(f"Processing error: {e}")
        reply_message(reply_token, TextMessage(text="حدث خطأ. حاول مرة أخرى"))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def on_message(event):
    executor.submit(process_message, event.source.user_id, event.message.text, event.reply_token)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_games": game_mgr.count_active()
    })

@app.route("/")
def index():
    return "Bot Mesh v15.0 - Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=(Config.ENV == "development"))
