import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction
)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

def askTimeSlot(data):
    message = TemplateSendMessage(
        alt_text='時間帯',
        template=ButtonsTemplate(
        title='時間帯',
        text='時間帯を選択してください',
        actions=[
            PostbackTemplateAction(
                label='午前中',
                text='午前中',
                data='phase=time&{}&time=beforenoon'.format(data)
            ),
            PostbackTemplateAction(
                label='午後',
                text='午後',
                data='phase=time&{}&time=afternoon'.format(data)
            ),
            PostbackTemplateAction(
                label='一日中',
                text='一日中',
                data='phase=time&{}&time=fulltime'.format(data)
            ),
        ])
    )

    return message

def askBudget(data):
    message = TemplateSendMessage(
        alt_text='予算',
        template=ButtonsTemplate(
        title='予算',
        text='予算を選択してください',
        actions=[
            PostbackTemplateAction(
                label='2万',
                text='2万',
                data='phase=budget&{}&budget=2'.format(data)
            ),
            PostbackTemplateAction(
                label='3万',
                text='3万',
                data='phase=budget&{}&budget=3'.format(data)
            ),
            PostbackTemplateAction(
                label='4万',
                text='4万',
                data='phase=budget&{}&budget=4'.format(data)
            ),
        ])
    )

    return message

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "こんにちは":
        line_bot_api.reply_message(
        event.reply_token,
        askBudget("hoge=huga"))

@handler.add(PostbackEvent)
def handle_postback(event):

    query = event.postback.data
    #TODO queryをパース key1=value1&key2=value2... の形式

    reply = askTimeSlot("hoge=huga")

    line_bot_api.reply_message(
        event.reply_token,
        reply
    )

if __name__ == "__main__":
    app.run(debug=True)
