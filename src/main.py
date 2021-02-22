import json
import requests
from keys import TELE_TOKEN


URL = "https://api.telegram.org/bot{}/".format(TELE_TOKEN)

def send_message(text, chat_id):
    final_text = "You said: " + text
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)

def lambda_handler(event, context):
    message = json.loads(event['body'])
    chat_id = message['message']['chat']['id']
    print(chat_id)
    # reply = message['message']['text']
    print(message['message'])
    image = requests.get("https://avatars.githubusercontent.com/u/9259160?s=460&u=a363b29339e611e13e1f71ea7552e8bf5914cf37&v=4")
    file = open("/tmp/sample_image.png", "wb")
    file.write(image.content)
    file.close()
    files = {'photo': open("/tmp/sample_image.png", "rb")}
    requests.post(URL + "sendPhoto?chat_id={}".format(chat_id), files=files)
    # send_message(reply, chat_id)
    return {
        'statusCode': 200
    }
