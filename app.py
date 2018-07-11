import os
from flask import Flask, request, abort
import urllib
from tinydb import TinyDB, Query

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, CarouselTemplate, CarouselColumn,
    MessageTemplateAction, URITemplateAction, PostbackTemplateAction
)

app = Flask(__name__)

db = TinyDB('./db.json')
Course = Query()

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
                data='phase=time&{}&time=午前中'.format(data)
            ),
            PostbackTemplateAction(
                label='午後',
                text='午後',
                data='phase=time&{}&time=午後'.format(data)
            ),
            PostbackTemplateAction(
                label='一日中',
                text='一日中',
                data='phase=time&{}&time=一日中'.format(data)
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

def getCourses(location, timeslot, budget):
    results = db.search((Course.location == location) & (Course.timeslot == timeslot))
    courses = [
            CarouselColumn(
                thumbnail_image_url=course["image"],
                title=course["title"],
                text=course["description"],
                actions=[
                    URITemplateAction(
                        label='webサイトへ飛ぶ',
                        uri=course["url"]
                    )
                ]
            )
            for course in results]
        
    return courses

def resultsTemplate(data):

    query = parseQuery(data)

    #TODO クエリからデートコース一覧を取得
    # courses = ...

    location = query["location"][0]
    timeslot = query["time"][0]
    budget = query["budget"][0]

    courses = getCourses(location, timeslot, budget)

    if len(courses) == 1:
        courses = courses * 2

    if courses:
        message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=courses
        ))

        return message
    else:
        return TextSendMessage(text="残念ですがご希望の条件に合ったデートコースが見つかりませんでした。")
        


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

locations = ["横浜", "鎌倉", "恵比寿", "銀座", "お台場", "浅草"]

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    text = event.message.text
    if text in locations:

        line_bot_api.reply_message(
        event.reply_token,
        askTimeSlotTemplate("location={}".format(text)))

@handler.add(MessageEvent)
def handle_location(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    print(event.message.id)
    if latitude == 35.631775 and longitude == 139.777733:
        line_bot_api.reply_message(
        event.reply_token,
        askTimeSlotTemplate("location=お台場"))

@handler.add(PostbackEvent)
def handle_postback(event):
    reply = None

    data = event.postback.data
    query =  parseQuery(data)
    if query["phase"][0] == "budget":
        reply = resultsTemplate(data)
    elif query["phase"][0] == "time":
        reply = askBudgetTemplate(data)
    #TODO
    #else:
    #    reply =  エラーメッセージを登録

    try:
        line_bot_api.reply_message(
            event.reply_token,
            reply
        )
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
        print(e)


if __name__ == "__main__":
    app.run(debug=True)
