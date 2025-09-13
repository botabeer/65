from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# جلب التوكن والسر من Environment Variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# أوامر الأدمن
ADMINS = ["Ub0345b01633bbe470bb6ca45ed48a913"]  # ضع userId هنا

@app.route("/api/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    # أمر استخراج الـ ID
    if msg.lower() == "id":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"📌 userId الخاص بك هو:\n{user_id}")
        )
        return

    # أمر للقفل
    if msg == "قفل القروب" and user_id in ADMINS:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ تم قفل القروب بواسطة الأدمن")
        )
        return

    # رد افتراضي
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"استقبلت رسالتك: {msg}")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
