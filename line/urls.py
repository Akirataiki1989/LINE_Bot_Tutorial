import sys, requests

from fastapi import APIRouter, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from . import message_event, user_event

sys.path.append(".")

import config

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
imgbb_api_key = config.IMGBB_KEY

line_app = APIRouter()

@line_app.post("/callback")
async def callback(request: Request) -> str:
    """LINE Bot webhook callback

    Args:
        request (Request): Request Object.

    Raises:
        HTTPException: Invalid Signature Error

    Returns:
        str: OK
    """
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    
    # handle webhook body
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameter")
    return "OK"


@handler.add(FollowEvent)
def handle_follow(event) -> None:
    """Event - User follow LINE Bot

    Args:
        event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#follow-event
    """
    user_event.handle_follow(event=event)


@handler.add(UnfollowEvent)
def handle_unfollow(event) -> None:
    """Event - User ban LINE Bot

    Args:
        event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#unfollow-event
    """
    user_event.handle_unfollow(event=event)


@handler.add(MessageEvent, message=(TextMessage))
def handle_message(event) -> None:
    """Event - User sent message

    Args:
        event (LINE Event Object): Refer to https://developers.line.biz/en/reference/messaging-api/#message-event
    """
    message_event.handle_message(event=event)

@line_app.post("/push_message")
async def push_msg(user_id:str, message_str:str) -> str:
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message_str))
        return "OK"
    except Exception as e:
        raise e

@line_app.post("/send_picture")
async def send_img(user_id:str, expiration:str, img_base64:str) -> str:
    params = {'expiration': expiration,'key': imgbb_api_key}
    files = {'image': (None, img_base64)}
    response = requests.post('https://api.imgbb.com/1/upload', params=params, files=files)
    response_data = response.json()
    img_url = response_data['data']['url']
    img_thumb_url = response_data['data']['thumb']['url']
    try:
        line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=img_url, preview_image_url=img_thumb_url))
        return "OK"
    except Exception as e:
        raise e
    '''
    {
    "data": {
        "id": "2ndCYJK",
        "title": "c1f64245afb2",
        "url_viewer": "https://ibb.co/2ndCYJK",
        "url": "https://i.ibb.co/w04Prt6/c1f64245afb2.gif",
        "display_url": "https://i.ibb.co/98W13PY/c1f64245afb2.gif",
        "width":"1",
        "height":"1",
        "size": "42",
        "time": "1552042565",
        "expiration":"0",
        "image": {
        "filename": "c1f64245afb2.gif",
        "name": "c1f64245afb2",
        "mime": "image/gif",
        "extension": "gif",
        "url": "https://i.ibb.co/w04Prt6/c1f64245afb2.gif",
        },
        "thumb": {
        "filename": "c1f64245afb2.gif",
        "name": "c1f64245afb2",
        "mime": "image/gif",
        "extension": "gif",
        "url": "https://i.ibb.co/2ndCYJK/c1f64245afb2.gif",
        }
    '''