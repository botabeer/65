from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage
import threading
import time
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, SYSTEM_SETTINGS, BOT_NAME, BOT_VERSION
from handlers import MessageHandler
from database import db
from game_loader import game_loader
from utils import setup_logging

logger = setup_logging()

app = Flask(__name__)

try:
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)
    message_handler = MessageHandler(line_bot_api)
    logger.info(f"{BOT_NAME} v{BOT_VERSION} - LINE API initialized")
except Exception as e:
    logger.error(f"Failed to initialize LINE API: {e}")
    raise

games_count = game_loader.load_games()
logger.info(f"Loaded {games_count} games from games folder")

@app.route("/", methods=['GET'])
def home():
    return f"{BOT_NAME} v{BOT_VERSION} - Running", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    
    if not signature:
        logger.warning("Missing X-Line-Signature header")
        abort(400)
    
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature detected")
        abort(400)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    try:
        messages = message_handler.handle_message(event)
        
        if messages:
            line_bot_api.reply_message(event.reply_token, messages)
    
    except LineBotApiError as e:
        logger.error(f"LINE API Error: {e.status_code} - {e.error.message}")
    except Exception as e:
        logger.error(f"Error in message handler: {e}", exc_info=True)

def cleanup_task():
    logger.info("Cleanup task started")
    
    while True:
        try:
            time.sleep(3600)
            
            if SYSTEM_SETTINGS['clean_old_sessions']:
                deleted = db.cleanup_old_sessions(SYSTEM_SETTINGS['session_cleanup_hours'])
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} old sessions")
        
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info(f"{BOT_NAME} v{BOT_VERSION} - Starting")
    logger.info(f"Security spam protection: {SYSTEM_SETTINGS.get('enable_spam_protection', False)}")
    logger.info(f"Games loaded: {games_count}")
    
    if SYSTEM_SETTINGS['clean_old_sessions']:
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
    
    port = SYSTEM_SETTINGS.get('port', 5000)
    logger.info(f"{BOT_NAME} started successfully on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
