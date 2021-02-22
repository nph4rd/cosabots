"""
Handler code for the lambda
"""

import json

import requests

from keys import TELE_TOKEN

URL = f"https://api.telegram.org/bot{TELE_TOKEN}/"
FILE_URL = "https://api.telegram.org/file/bot{TELE_TOKEN}/"


def send_message(text, chat_id):
    """
    Send a message with {text} to chat with {chat_id}
    """
    final_text = "You said: " + text
    url = URL + f"sendMessage?text={final_text}&chat_id={chat_id}"
    requests.get(url)


def lambda_handler(event, context):
    """
    Handle basic bot functionality
    """
    message = json.loads(event["body"])
    chat_id = message["message"]["chat"]["id"]
    try:
        file_id = message["photo"][0]["file_id"]
    except KeyError as err:
        print(f"There was no photo. Error: {err}")
    print(message["message"])
    image = requests.get(FILE_URL + str(file_id))
    file = open("/tmp/image.png", "wb")
    file.write(image.content)
    file.close()
    files = {"photo": open("/tmp/image.png", "rb")}
    requests.post(URL + "sendPhoto?chat_id={}".format(chat_id), files=files)
    return {"statusCode": 200}
