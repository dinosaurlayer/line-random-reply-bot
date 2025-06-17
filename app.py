from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os, random, datetime

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

# 記錄使用者發送次數：{user_id: {"date": "YYYY-MM-DD", "count": N}}
user_usage = {}

# ✅ 健康檢查 (Render health check 用)
@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

# ✅ 處理 LINE 傳進來的 POST 請求
@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return "OK"

# ✅ 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 初始化使用者資料
    if user_id not in user_usage:
        user_usage[user_id] = {"date": today, "count": 0}

    # 如果日期變了就重設
    if user_usage[user_id]["date"] != today:
        user_usage[user_id] = {"date": today, "count": 0}

    # 超過 5 次就不回應
    if user_usage[user_id]["count"] >= 5:
        return

    # 增加使用次數
    user_usage[user_id]["count"] += 1

    # 回覆用語錄
    replies = [
        "你知道你在跟誰說話嗎!",
        "不想回你，但我還是回了，所以我是愛你的",
        "我不想聽!",
        "我不是你的朋友嗎?",
        "請問你是在發表高見嗎？",
        "我已經沒有感情了，只剩下 if 和 else。",
        "你不餓嗎?",
        "喔! 是喔!",
        "對不起嘛~",
        "我是愛你的"
    ]

    # 滿 5 次則改回上限通知
    if user_usage[user_id]["count"] == 5:
        msg = "你今天的回覆次數已達上限，請明天再來～"
    else:
        msg = random.choice(replies)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg)
    )
