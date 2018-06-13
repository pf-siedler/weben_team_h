import os
from flask import Flask, request, abort
import urllib

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, CarouselTemplate, CarouselColumn,
    MessageTemplateAction, URITemplateAction, PostbackTemplateAction
)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

def askTimeSlotTemplate(data):
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

parseQuery = lambda s: urllib.parse.parse_qs(s)

def askBudgetTemplate(data):
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

def resultsTemplate(data):

    query = parseQuery(data)

    #TODO クエリからデートコース一覧を取得
    # courses = ...

    place = query["place"][0]
    timeslot = query["time"][0]
    budget = query["budget"][0]

    courses = [
            CarouselColumn(
                thumbnail_image_url='https://example.com/item1.jpg',
                title='this is menu1',
                text='場所{} 時間帯{} 予算{}のイベント一覧'.format(place, timeslot, budget),
                actions=[
                    PostbackTemplateAction(
                        label='postback1',
                        text='postback text1',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='message1',
                        text='message text1'
                    ),
                    URITemplateAction(
                        label='uri1',
                        uri='http://example.com/1'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://example.com/item2.jpg',
                title='this is menu2',
                text='description2',
                actions=[
                    PostbackTemplateAction(
                        label='postback2',
                        text='postback text2',
                        data='action=buy&itemid=2'
                    ),
                    MessageTemplateAction(
                        label='message2',
                        text='message text2'
                    ),
                    URITemplateAction(
                        label='uri2',
                        uri='http://example.com/2'
                    )
                ]
            )
        ]

    message = TemplateSendMessage(
    alt_text='Carousel template',
    template=CarouselTemplate(
        columns=courses
    ))

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

places = ["横浜", "東京", "鎌倉"]

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text in places:

        line_bot_api.reply_message(
        event.reply_token,
        askTimeSlotTemplate("place={}".format(text)))

@handler.add(PostbackEvent)
def handle_postback(event):
    reply = None

    data = event.postback.data
    query =  parseQuery(data)
    print(query)
    if query["phase"][0] == "budget":
        reply = resultsTemplate(data)
    elif query["phase"][0] == "time":
        reply = askBudgetTemplate(data)
    #TODO
    #else:
    #    reply =  エラーメッセージを登録

    line_bot_api.reply_message(
        event.reply_token,
        reply
    )

if __name__ == "__main__":
    app.run(debug=True)
