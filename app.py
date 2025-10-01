from flask import Flask, request, abort
import os
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

try:
    bot_info = line_bot_api.get_bot_info()
    BOT_ID = bot_info.user_id
except Exception:
    BOT_ID = "غير متاح (تاكد من التوكن)"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    group_id = None
    if event.source.type == "group":
        group_id = event.source.group_id
    elif event.source.type == "room":
        group_id = event.source.room_id
    text = event.message.text.strip().lower()
    reply_text = None

    if text in ["id", "معرفي"]:
        reply_text = f"🆔 USER ID: {user_id.upper()}"
    elif text in ["idg", "معرف_القروب"]:
        if group_id:
            reply_text = f"🆔 GROUP/ROOM ID: {group_id.upper()}"
        else:
            reply_text = "❌ هذا الامر يعمل فقط داخل قروب او روم"
    elif text in ["help", "مساعدة"]:
        reply_text = (
            "\u202B📌 اوامر البوت:\n\n"
            "• يظهر معرفك / ID\n"
            "• يظهر معرف القروب او الروم / IDG\n"
            "• عرض الاوامر / HELP"
        )

    if reply_text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
