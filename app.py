from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import logging

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, BOT_NAME, BOT_VERSION
from core import MessageHandler
from database import db
from game_loader import game_loader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

message_handler = MessageHandler(line_bot_api, configuration)

games_count = game_loader.load_games()
logger.info(f"{BOT_NAME} v{BOT_VERSION} - {games_count} games loaded")

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
        logger.warning("Missing signature")
        return "OK", 200
    
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return "OK", 200
    
    return "OK", 200

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    try:
        messages = message_handler.handle_message(event)
        if messages:
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
            )
    except Exception as e:
        logger.error(f"Message handling error: {e}", exc_info=True)

@handler.default()
def default_handler(event):
    try:
        if hasattr(event, 'type'):
            if event.type == 'follow':
                messages = message_handler.handle_follow(event)
                if messages:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
                    )
            elif event.type == 'join':
                messages = message_handler.handle_join(event)
                if messages:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
                    )
    except Exception as e:
        logger.error(f"Event handling error: {e}", exc_info=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
