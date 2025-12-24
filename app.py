from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os, threading, time

from config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
    SYSTEM_SETTINGS,
    BOT_NAME,
    BOT_VERSION
)
from handlers import MessageHandler
from database import db
from game_loader import game_loader
from utils import setup_logging

logger = setup_logging()
app = Flask(__name__)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

message_handler = MessageHandler(line_bot_api, configuration)

logger.info(f"{BOT_NAME} v{BOT_VERSION} - LINE API ready")

games_count = game_loader.load_games()
logger.info(f"Games loaded: {games_count}")

@app.route("/", methods=["GET"])
def home():
    return f"{BOT_NAME} v{BOT_VERSION} - Running", 200

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        abort(400)

    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        logger.error("Webhook error", exc_info=True)

    return "OK", 200

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        messages = message_handler.handle_message(event)
        if messages:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )
    except Exception:
        logger.error("Message handling error", exc_info=True)

def cleanup_task():
    logger.info("Cleanup task started")
    while True:
        time.sleep(3600)
        try:
            deleted = db.cleanup_old_sessions(
                SYSTEM_SETTINGS["session_cleanup_hours"]
            )
            if deleted:
                logger.info(f"Cleaned {deleted} sessions")
        except Exception:
            logger.error("Cleanup error", exc_info=True)

if __name__ == "__main__":
    logger.info(f"{BOT_NAME} v{BOT_VERSION} starting")

    if SYSTEM_SETTINGS.get("clean_old_sessions"):
        if os.getenv("RUN_MAIN") == "true":
            threading.Thread(
                target=cleanup_task,
                daemon=True
            ).start()

    port = int(os.environ.get("PORT", SYSTEM_SETTINGS.get("port", 5000)))
    app.run(host="0.0.0.0", port=port)
