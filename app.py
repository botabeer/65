from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
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
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
    message_handler = MessageHandler(line_bot_api, configuration)
    logger.info(f"{BOT_NAME} v{BOT_VERSION} - LINE API initialized")
except Exception as e:
    logger.error(f"Failed to initialize LINE API: {e}")
    raise

games_count = game_loader.load_games()
logger.info(f"Loaded {games_count} games from games folder")

@app.route("/", methods=['GET'])
def home():
    return f"{BOT_NAME} v{BOT_VERSION} - Running", 200

@app.route("/health", methods=['GET'])
def health():
    return "OK", 200

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        messages = message_handler.handle_message(event)
        if messages:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=messages))
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
