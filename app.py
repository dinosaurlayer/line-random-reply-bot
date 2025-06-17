from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os, random, datetime

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

# 記錄使用者發送次數：格式為 {user_id: {"date": "2025-06-18", "count": 2}}
user_usage = {}

@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 沒記錄過此人，初始化
    if user_id not in user_usage:
        user_usage[user_id] = {"date": today, "count": 0}

    # 如果是昨天的資料，重置計數
    if user_usage[user_id]["date"] != today:
        user_usage[user_id] = {"date": today, "count": 0}

    # 超過 5 次不再回覆
    if user_usage[user_id]["count"] >= 5:
        return

    # 計數 +1
    user_usage[user_id]["count"] += 1

    replies = [
        "你知道你在跟誰說話嗎!"
        "不想回你，但我還是回了，所以我是愛你的"
        "我不想聽!"
        "我不是你的朋友嗎?"
        "請問你是在發表高見嗎？",
        "我已經沒有感情了，只剩下 if 和 else。"
        "你不餓嗎?"
        "喔!是喔!"
        "對不起嘛~"
        "我是愛你的"
    ]

    # 如果滿了就回：已達上限
    if user_usage[user_id]["count"] == 3:
        msg = "你今天的回覆次數已達上限，請明天再來～"
    else:
        msg = random.choice(replies)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg)
    )
