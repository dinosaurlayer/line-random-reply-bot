from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random

app = Flask(__name__)

# 從環境變數讀取 LINE Channel Token 和 Secret
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

# 建立 LINE API 實例
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 健康檢查用
@app.route("/", methods=["GET"])
def health_check():
    return "LINE bot is running!", 200

# 處理 LINE 訊息
@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK", 200

# 收到文字訊息時隨機回覆
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    replies = [
        "你說什麼？",
        "我就爛",
        "再說一次看看？",
        "嗯嗯我聽到了（但我不懂）",
        "我不知道你在說什麼欸哈哈"
    ]
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=random.choice(replies))
    )

# 啟動 Flask（Render 會自動呼叫此入口）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 會設 PORT 環境變數
    app.run(host="0.0.0.0", port=port)
