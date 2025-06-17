from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os, random
from datetime import datetime

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

# 建立記錄使用者回覆次數的字典
user_reply_count = {}

@app.route("/", methods=["GET"])
def health_check():
    return "LINE bot is running!", 200

@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    today = datetime.now().strftime("%Y-%m-%d")

    # 初始化記錄
    if user_id not in user_reply_count:
        user_reply_count[user_id] = {}
    if user_reply_count[user_id].get("date") != today:
        user_reply_count[user_id] = {"date": today, "count": 0}

    # 檢查次數限制
    if user_reply_count[user_id]["count"] >= 3:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你今天的回覆次數已達上限，請明天再來！")
        )
        return

    # 正常回覆
    replies = ["我就爛", "你說什麼？", "再說一次看看？"]
    reply_text = random.choice(replies)

    user_reply_count[user_id]["count"] += 1  # 加次數

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
